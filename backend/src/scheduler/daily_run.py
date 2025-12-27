"""
Daily run orchestrator Lambda.

File Name      : daily_run.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
from typing import Dict, Any, List
from datetime import datetime, date
import traceback

from src.db import DynamoDBClient
from src.db.models import AgentType, User
from src.agents import (
    BuffettAgent, GrahamAgent, LynchAgent,
    DalioAgent, BogleAgent, WoodAgent
)
from src.alerts.ses_client import send_daily_summary
from src.utils import get_logger

logger = get_logger(__name__)

AGENT_CLASSES = {
    AgentType.BUFFETT: BuffettAgent,
    AgentType.GRAHAM: GrahamAgent,
    AgentType.LYNCH: LynchAgent,
    AgentType.DALIO: DalioAgent,
    AgentType.BOGLE: BogleAgent,
    AgentType.WOOD: WoodAgent,
}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for daily scheduled runs.

    Triggered by EventBridge at 9 AM EST on market days.
    Runs all 6 agents for all users.
    """
    logger.info("Starting daily agent runs")
    start_time = datetime.utcnow()

    if not _is_market_day():
        logger.info("Not a market day, skipping")
        return {"statusCode": 200, "body": "Market closed"}

    try:
        db = DynamoDBClient()
        users = _get_all_users(db)

        results = []
        for user in users:
            user_results = _run_agents_for_user(db, user)
            results.append({
                "user_id": user.user_id,
                "results": user_results,
            })

            if user.email_alerts_enabled:
                _send_user_summary(user, user_results)

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Completed all runs in {duration:.1f}s")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "users_processed": len(users),
                "duration_seconds": duration,
                "results": results,
            })
        }

    except Exception as exc:
        logger.error(f"Daily run failed: {exc}\n{traceback.format_exc()}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)})
        }


def _is_market_day() -> bool:
    """Check if today is a market day (weekday)."""
    today = date.today()
    return today.weekday() < 5


def _get_all_users(db: DynamoDBClient) -> List[User]:
    """Get all users from database."""
    # In production, would scan/query users table
    # For MVP, return empty list (users created on first API call)
    return []


def _run_agents_for_user(
    db: DynamoDBClient,
    user: User
) -> List[Dict[str, Any]]:
    """Run all agents for a single user."""
    results = []

    for agent_type, agent_class in AGENT_CLASSES.items():
        try:
            agent = agent_class(db_client=db)
            run = agent.run(user.user_id)

            results.append({
                "agent": agent_type.value,
                "status": "success",
                "run_id": run.run_id,
                "trades": len(run.executed_trades),
                "value_change": run.portfolio_value_after - run.portfolio_value_before,
            })

        except Exception as exc:
            logger.error(f"Agent {agent_type.value} failed for {user.user_id}: {exc}")
            results.append({
                "agent": agent_type.value,
                "status": "error",
                "error": str(exc),
            })

    return results


def _send_user_summary(user: User, results: List[Dict[str, Any]]) -> None:
    """Send daily summary email to user."""
    try:
        trades_today = sum(r.get("trades", 0) for r in results if r["status"] == "success")
        if trades_today > 0:
            send_daily_summary(user.email, results)
    except Exception as exc:
        logger.error(f"Failed to send summary to {user.email}: {exc}")

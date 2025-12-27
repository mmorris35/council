"""
Dashboard API Lambda handler.

File Name      : dashboard.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
from typing import Dict, Any
from datetime import datetime

from src.db import DynamoDBClient
from src.db.models import AgentType
from src.utils import get_logger

logger = get_logger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for dashboard endpoints.

    Routes:
    - GET /dashboard - Get overview of all agents
    - GET /agents/{agent_id} - Get agent details
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}

    user_id = _get_user_id(event)
    if not user_id:
        return _response(401, {"error": "Unauthorized"})

    try:
        db = DynamoDBClient()

        if path == "/dashboard" and http_method == "GET":
            return _get_dashboard(db, user_id)

        elif "/agents/" in path and http_method == "GET":
            agent_id = path_params.get("agent_id")
            return _get_agent_detail(db, user_id, agent_id)

        return _response(404, {"error": "Not found"})

    except Exception as exc:
        logger.error(f"Dashboard error: {exc}")
        return _response(500, {"error": str(exc)})


def _get_dashboard(db: DynamoDBClient, user_id: str) -> Dict[str, Any]:
    """Get dashboard overview."""
    agents_summary = []

    for agent_type in AgentType:
        portfolio = db.get_portfolio(user_id, agent_type)
        latest_run = db.get_latest_agent_run(agent_type)

        summary = {
            "agent_type": agent_type.value,
            "agent_name": _get_agent_name(agent_type),
            "portfolio_value": portfolio.total_value if portfolio else 0,
            "cash": portfolio.cash if portfolio else 0,
            "num_positions": len(portfolio.positions) if portfolio else 0,
            "last_run": latest_run.run_date.isoformat() if latest_run else None,
            "last_analysis": latest_run.analysis[:200] if latest_run else None,
        }
        agents_summary.append(summary)

    total_value = sum(a["portfolio_value"] for a in agents_summary)

    return _response(200, {
        "user_id": user_id,
        "total_value": total_value,
        "agents": agents_summary,
        "generated_at": datetime.utcnow().isoformat(),
    })


def _get_agent_detail(
    db: DynamoDBClient,
    user_id: str,
    agent_id: str
) -> Dict[str, Any]:
    """Get detailed view of a single agent."""
    try:
        agent_type = AgentType(agent_id)
    except ValueError:
        return _response(400, {"error": f"Invalid agent: {agent_id}"})

    portfolio = db.get_portfolio(user_id, agent_type)
    runs = db.get_agent_runs(agent_type, limit=10)
    transactions = db.get_user_transactions(user_id, limit=20)
    agent_txns = [t for t in transactions if t.agent_type == agent_type]

    positions = []
    if portfolio:
        for pos in portfolio.positions:
            positions.append({
                "symbol": pos.symbol,
                "shares": pos.shares,
                "avg_cost": pos.avg_cost,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "gain_loss": pos.gain_loss,
                "gain_loss_pct": pos.gain_loss_pct * 100,
            })

    return _response(200, {
        "agent_type": agent_type.value,
        "agent_name": _get_agent_name(agent_type),
        "portfolio": {
            "total_value": portfolio.total_value if portfolio else 0,
            "cash": portfolio.cash if portfolio else 0,
            "positions": positions,
        },
        "recent_runs": [
            {
                "run_id": r.run_id,
                "date": r.run_date.isoformat(),
                "analysis": r.analysis,
                "recommendations": r.recommendations,
                "trades_executed": len(r.executed_trades),
                "value_before": r.portfolio_value_before,
                "value_after": r.portfolio_value_after,
            }
            for r in runs
        ],
        "recent_transactions": [
            {
                "transaction_id": t.transaction_id,
                "type": t.transaction_type.value,
                "symbol": t.symbol,
                "shares": t.shares,
                "price": t.price,
                "reasoning": t.reasoning,
                "date": t.created_at.isoformat(),
            }
            for t in agent_txns[:10]
        ],
    })


def _get_agent_name(agent_type: AgentType) -> str:
    """Get display name for agent."""
    names = {
        AgentType.BUFFETT: "Warren Buffett",
        AgentType.GRAHAM: "Benjamin Graham",
        AgentType.LYNCH: "Peter Lynch",
        AgentType.DALIO: "Ray Dalio",
        AgentType.BOGLE: "John Bogle",
        AgentType.WOOD: "Cathie Wood",
    }
    return names.get(agent_type, agent_type.value)


def _get_user_id(event: Dict[str, Any]) -> str:
    """Extract user ID from Cognito authorizer."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub", "")


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Build API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }

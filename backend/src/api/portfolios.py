"""
Portfolio API Lambda handler.

File Name      : portfolios.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
from typing import Dict, Any

from src.db import DynamoDBClient
from src.db.models import AgentType
from src.utils import get_logger

logger = get_logger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for portfolio endpoints.

    Routes:
    - GET /portfolios - List all user portfolios
    - GET /portfolios/{portfolio_id} - Get specific portfolio
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}

    user_id = _get_user_id(event)
    if not user_id:
        return _response(401, {"error": "Unauthorized"})

    try:
        db = DynamoDBClient()

        if path == "/portfolios" and http_method == "GET":
            return _list_portfolios(db, user_id)

        elif "/portfolios/" in path and http_method == "GET":
            portfolio_id = path_params.get("portfolio_id")
            return _get_portfolio(db, user_id, portfolio_id)

        return _response(404, {"error": "Not found"})

    except Exception as exc:
        logger.error(f"Portfolio error: {exc}")
        return _response(500, {"error": str(exc)})


def _list_portfolios(db: DynamoDBClient, user_id: str) -> Dict[str, Any]:
    """List all portfolios for user."""
    portfolios = db.get_user_portfolios(user_id)

    result = []
    for portfolio in portfolios:
        result.append({
            "portfolio_id": portfolio.portfolio_id,
            "agent_type": portfolio.agent_type.value,
            "total_value": portfolio.total_value,
            "cash": portfolio.cash,
            "num_positions": len(portfolio.positions),
            "updated_at": portfolio.updated_at.isoformat(),
        })

    return _response(200, {
        "portfolios": result,
        "total_count": len(result),
    })


def _get_portfolio(
    db: DynamoDBClient,
    user_id: str,
    portfolio_id: str
) -> Dict[str, Any]:
    """Get specific portfolio by ID."""
    portfolios = db.get_user_portfolios(user_id)
    portfolio = next(
        (p for p in portfolios if p.portfolio_id == portfolio_id),
        None
    )

    if not portfolio:
        return _response(404, {"error": "Portfolio not found"})

    positions = []
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
        "portfolio_id": portfolio.portfolio_id,
        "agent_type": portfolio.agent_type.value,
        "cash": portfolio.cash,
        "total_value": portfolio.total_value,
        "positions": positions,
        "created_at": portfolio.created_at.isoformat(),
        "updated_at": portfolio.updated_at.isoformat(),
    })


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

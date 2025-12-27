"""
Auth API Lambda handler.

File Name      : auth.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
import uuid
from typing import Dict, Any

from src.db import DynamoDBClient
from src.db.models import User, AgentType, Portfolio
from src.utils import get_logger, settings

logger = get_logger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for auth endpoints.

    Routes:
    - POST /auth/register - Register/initialize user
    - GET /auth/profile - Get user profile
    - PUT /auth/profile - Update user profile
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "")

    user_id = _get_user_id(event)
    if not user_id:
        return _response(401, {"error": "Unauthorized"})

    try:
        db = DynamoDBClient()

        if path == "/auth/register" and http_method == "POST":
            return _register_user(db, user_id, event)

        elif path == "/auth/profile" and http_method == "GET":
            return _get_profile(db, user_id)

        elif path == "/auth/profile" and http_method == "PUT":
            return _update_profile(db, user_id, event)

        return _response(404, {"error": "Not found"})

    except Exception as exc:
        logger.error(f"Auth error: {exc}")
        return _response(500, {"error": str(exc)})


def _register_user(
    db: DynamoDBClient,
    user_id: str,
    event: Dict[str, Any]
) -> Dict[str, Any]:
    """Register/initialize a new user with portfolios."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    email = claims.get("email", "")

    existing = db.get_user(user_id)
    if existing:
        return _response(200, {
            "message": "User already exists",
            "user_id": user_id,
        })

    user = User(user_id=user_id, email=email)
    db.create_user(user)

    for agent_type in AgentType:
        portfolio = Portfolio(
            portfolio_id=str(uuid.uuid4()),
            user_id=user_id,
            agent_type=agent_type,
            cash=settings.starting_portfolio_value,
            positions=[],
        )
        db.save_portfolio(portfolio)

    logger.info(f"Registered user {user_id} with 6 portfolios")

    return _response(201, {
        "message": "User registered successfully",
        "user_id": user_id,
        "portfolios_created": 6,
        "starting_value": settings.starting_portfolio_value,
    })


def _get_profile(db: DynamoDBClient, user_id: str) -> Dict[str, Any]:
    """Get user profile."""
    user = db.get_user(user_id)

    if not user:
        return _response(404, {"error": "User not found"})

    portfolios = db.get_user_portfolios(user_id)
    total_value = sum(p.total_value for p in portfolios)

    return _response(200, {
        "user_id": user.user_id,
        "email": user.email,
        "email_alerts_enabled": user.email_alerts_enabled,
        "created_at": user.created_at.isoformat(),
        "total_portfolio_value": total_value,
        "num_portfolios": len(portfolios),
    })


def _update_profile(
    db: DynamoDBClient,
    user_id: str,
    event: Dict[str, Any]
) -> Dict[str, Any]:
    """Update user profile settings."""
    user = db.get_user(user_id)

    if not user:
        return _response(404, {"error": "User not found"})

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    if "email_alerts_enabled" in body:
        user.email_alerts_enabled = bool(body["email_alerts_enabled"])

    db.create_user(user)

    return _response(200, {
        "message": "Profile updated",
        "email_alerts_enabled": user.email_alerts_enabled,
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

"""
Tests for Dashboard API.

File Name      : test_api_dashboard.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.api.dashboard import handler, _get_agent_name
from src.db.models import AgentType, Portfolio, Position, AgentRun


class TestDashboardAPI:
    """Tests for Dashboard API."""

    @pytest.fixture
    def mock_event(self):
        return {
            "httpMethod": "GET",
            "path": "/dashboard",
            "pathParameters": None,
            "requestContext": {
                "authorizer": {
                    "claims": {"sub": "user123"}
                }
            }
        }

    @pytest.fixture
    def mock_portfolio(self):
        return Portfolio(
            portfolio_id="port1",
            user_id="user123",
            agent_type=AgentType.BUFFETT,
            cash=50000.0,
            positions=[
                Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
            ],
        )

    def test_unauthorized_without_user(self):
        """Test 401 when no user in claims."""
        event = {
            "httpMethod": "GET",
            "path": "/dashboard",
            "requestContext": {"authorizer": {"claims": {}}}
        }

        response = handler(event, None)

        assert response["statusCode"] == 401

    def test_get_dashboard_success(self, mock_event, mock_portfolio):
        """Test successful dashboard retrieval."""
        with patch("src.api.dashboard.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_portfolio.return_value = mock_portfolio
            mock_db.get_latest_agent_run.return_value = None
            mock_db_class.return_value = mock_db

            response = handler(mock_event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert "agents" in body
            assert len(body["agents"]) == 6

    def test_get_agent_detail(self, mock_portfolio):
        """Test agent detail endpoint."""
        event = {
            "httpMethod": "GET",
            "path": "/agents/buffett",
            "pathParameters": {"agent_id": "buffett"},
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }

        with patch("src.api.dashboard.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_portfolio.return_value = mock_portfolio
            mock_db.get_agent_runs.return_value = []
            mock_db.get_user_transactions.return_value = []
            mock_db_class.return_value = mock_db

            response = handler(event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["agent_type"] == "buffett"

    def test_get_agent_name(self):
        """Test agent name lookup."""
        assert _get_agent_name(AgentType.BUFFETT) == "Warren Buffett"
        assert _get_agent_name(AgentType.BOGLE) == "John Bogle"

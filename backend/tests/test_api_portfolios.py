"""
Tests for Portfolio API.

File Name      : test_api_portfolios.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import json
from unittest.mock import MagicMock, patch

from src.api.portfolios import handler
from src.db.models import AgentType, Portfolio, Position


class TestPortfolioAPI:
    """Tests for Portfolio API."""

    @pytest.fixture
    def mock_portfolios(self):
        return [
            Portfolio(
                portfolio_id="port1",
                user_id="user123",
                agent_type=AgentType.BUFFETT,
                cash=50000.0,
                positions=[
                    Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
                ],
            ),
            Portfolio(
                portfolio_id="port2",
                user_id="user123",
                agent_type=AgentType.BOGLE,
                cash=30000.0,
                positions=[],
            ),
        ]

    def test_list_portfolios(self, mock_portfolios):
        """Test listing all portfolios."""
        event = {
            "httpMethod": "GET",
            "path": "/portfolios",
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }

        with patch("src.api.portfolios.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user_portfolios.return_value = mock_portfolios
            mock_db_class.return_value = mock_db

            response = handler(event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert len(body["portfolios"]) == 2

    def test_get_portfolio_by_id(self, mock_portfolios):
        """Test getting specific portfolio."""
        event = {
            "httpMethod": "GET",
            "path": "/portfolios/port1",
            "pathParameters": {"portfolio_id": "port1"},
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }

        with patch("src.api.portfolios.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user_portfolios.return_value = mock_portfolios
            mock_db_class.return_value = mock_db

            response = handler(event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["portfolio_id"] == "port1"

    def test_portfolio_not_found(self, mock_portfolios):
        """Test 404 for unknown portfolio."""
        event = {
            "httpMethod": "GET",
            "path": "/portfolios/unknown",
            "pathParameters": {"portfolio_id": "unknown"},
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }

        with patch("src.api.portfolios.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user_portfolios.return_value = mock_portfolios
            mock_db_class.return_value = mock_db

            response = handler(event, None)

            assert response["statusCode"] == 404

"""
Tests for Auth API.

File Name      : test_api_auth.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import json
from unittest.mock import MagicMock, patch

from src.api.auth import handler
from src.db.models import User


class TestAuthAPI:
    """Tests for Auth API."""

    @pytest.fixture
    def mock_event(self):
        return {
            "httpMethod": "POST",
            "path": "/auth/register",
            "body": "{}",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "user123",
                        "email": "test@example.com"
                    }
                }
            }
        }

    def test_register_new_user(self, mock_event):
        """Test registering a new user."""
        with patch("src.api.auth.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user.return_value = None
            mock_db.create_user.return_value = True
            mock_db.save_portfolio.return_value = True
            mock_db_class.return_value = mock_db

            response = handler(mock_event, None)

            assert response["statusCode"] == 201
            body = json.loads(response["body"])
            assert body["portfolios_created"] == 6
            assert mock_db.save_portfolio.call_count == 6

    def test_register_existing_user(self, mock_event):
        """Test registering when user already exists."""
        with patch("src.api.auth.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user.return_value = User(
                user_id="user123",
                email="test@example.com"
            )
            mock_db_class.return_value = mock_db

            response = handler(mock_event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert "already exists" in body["message"]

    def test_get_profile(self):
        """Test getting user profile."""
        event = {
            "httpMethod": "GET",
            "path": "/auth/profile",
            "requestContext": {
                "authorizer": {
                    "claims": {"sub": "user123"}
                }
            }
        }

        with patch("src.api.auth.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user.return_value = User(
                user_id="user123",
                email="test@example.com"
            )
            mock_db.get_user_portfolios.return_value = []
            mock_db_class.return_value = mock_db

            response = handler(event, None)

            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["user_id"] == "user123"

    def test_unauthorized_without_user(self):
        """Test 401 when no user in claims."""
        event = {
            "httpMethod": "GET",
            "path": "/auth/profile",
            "requestContext": {"authorizer": {"claims": {}}}
        }

        response = handler(event, None)

        assert response["statusCode"] == 401

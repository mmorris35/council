"""
Tests for scheduler.

File Name      : test_scheduler.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from src.scheduler.daily_run import handler, _is_market_day, _run_agents_for_user
from src.db.models import User


class TestScheduler:
    """Tests for daily scheduler."""

    def test_is_market_day_weekday(self, monkeypatch):
        """Test market day detection for weekday."""
        monkeypatch.setattr(
            "src.scheduler.daily_run.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 8)})  # Monday
        )
        assert _is_market_day() is True

    def test_is_market_day_weekend(self, monkeypatch):
        """Test market day detection for weekend."""
        monkeypatch.setattr(
            "src.scheduler.daily_run.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 6)})  # Saturday
        )
        assert _is_market_day() is False

    def test_run_agents_for_user(self):
        """Test running all agents for a user."""
        from src.db.models import AgentType

        mock_db = MagicMock()
        mock_db.get_portfolio.return_value = None
        mock_db.save_portfolio.return_value = True
        mock_db.save_agent_run.return_value = True
        mock_db.save_transaction.return_value = True

        user = User(user_id="test123", email="test@example.com")

        with patch("src.scheduler.daily_run.AGENT_CLASSES") as mock_agents:
            mock_agent = MagicMock()
            mock_run = MagicMock()
            mock_run.run_id = "run123"
            mock_run.executed_trades = []
            mock_run.portfolio_value_before = 100000
            mock_run.portfolio_value_after = 100500
            mock_agent.return_value.run.return_value = mock_run

            mock_agents.items.return_value = [(AgentType.BUFFETT, mock_agent)]

            results = _run_agents_for_user(mock_db, user)

            assert len(results) == 1
            assert results[0]["status"] == "success"

    def test_handler_skips_weekend(self, monkeypatch):
        """Test handler skips on weekends."""
        monkeypatch.setattr(
            "src.scheduler.daily_run.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 6)})
        )

        response = handler({}, None)

        assert response["statusCode"] == 200
        assert "closed" in response["body"]

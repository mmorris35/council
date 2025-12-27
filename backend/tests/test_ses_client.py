"""
Tests for SES client.

File Name      : test_ses_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import patch, MagicMock

from src.alerts.ses_client import send_daily_summary, send_trade_alert


class TestSESClient:
    """Tests for SES email client."""

    @pytest.fixture
    def mock_settings(self, monkeypatch):
        monkeypatch.setattr("src.alerts.ses_client.settings.ses_sender_email", "test@example.com")
        monkeypatch.setattr("src.alerts.ses_client.settings.aws_region", "us-east-1")

    def test_send_daily_summary(self, mock_settings):
        """Test daily summary email."""
        results = [
            {"agent": "buffett", "status": "success", "trades": 2, "value_change": 500},
            {"agent": "bogle", "status": "success", "trades": 0, "value_change": 100},
        ]

        with patch("boto3.client") as mock_boto:
            mock_ses = MagicMock()
            mock_ses.send_email.return_value = {"MessageId": "test123"}
            mock_boto.return_value = mock_ses

            result = send_daily_summary("user@example.com", results)

            assert result is True
            mock_ses.send_email.assert_called_once()

    def test_send_trade_alert(self, mock_settings):
        """Test trade alert email."""
        with patch("boto3.client") as mock_boto:
            mock_ses = MagicMock()
            mock_ses.send_email.return_value = {"MessageId": "test456"}
            mock_boto.return_value = mock_ses

            result = send_trade_alert(
                recipient="user@example.com",
                agent_name="Warren Buffett",
                trade_type="buy",
                symbol="AAPL",
                shares=100,
                price=175.50,
                reasoning="Strong moat and undervalued",
            )

            assert result is True

    def test_no_sender_configured(self, monkeypatch):
        """Test graceful handling when sender not configured."""
        monkeypatch.setattr("src.alerts.ses_client.settings.ses_sender_email", "")

        result = send_daily_summary("user@example.com", [])

        assert result is False

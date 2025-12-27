"""
Tests for FRED client.

File Name      : test_fred_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from src.data.fred_client import FREDClient, MacroDataPoint


class TestFREDClient:
    """Tests for FREDClient."""

    @pytest.fixture
    def client(self):
        return FREDClient(api_key="test_key")

    @pytest.fixture
    def mock_fred_response(self):
        return {
            "observations": [
                {"date": "2024-01-01", "value": "3.5"},
                {"date": "2024-02-01", "value": "3.4"},
                {"date": "2024-03-01", "value": "."},  # Missing data
                {"date": "2024-04-01", "value": "3.6"},
            ]
        }

    def test_get_series_success(self, client, mock_fred_response):
        """Test successful series fetch."""
        with patch.object(client.session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_fred_response
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = client.get_series("UNRATE")

            assert len(result) == 3  # Excludes missing "." value
            assert result[0].value == 3.5
            assert result[-1].value == 3.6

    def test_get_latest(self, client, mock_fred_response):
        """Test getting latest value."""
        with patch.object(client.session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_fred_response
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = client.get_latest("UNRATE")

            assert result is not None
            assert result.value == 3.6

    def test_no_api_key(self):
        """Test behavior without API key."""
        client = FREDClient(api_key=None)
        result = client.get_series("UNRATE")
        assert result == []

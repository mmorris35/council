"""
Tests for Yahoo Finance client.

File Name      : test_yfinance_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import patch, MagicMock
from src.data.yfinance_client import YFinanceClient, StockFundamentals


class TestYFinanceClient:
    """Tests for YFinanceClient."""

    @pytest.fixture
    def client(self):
        """Create a fresh client for each test."""
        return YFinanceClient()

    @pytest.fixture
    def mock_ticker_info(self):
        """Mock ticker info response."""
        return {
            "regularMarketPrice": 175.50,
            "trailingPE": 28.5,
            "priceToBook": 45.2,
            "marketCap": 2800000000000,
            "dividendYield": 0.005,
            "currentRatio": 1.0,
            "debtToEquity": 180,
            "sector": "Technology",
            "industry": "Consumer Electronics",
        }

    def test_get_fundamentals_success(self, client, mock_ticker_info):
        """Test successful fundamentals fetch."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker

            result = client.get_fundamentals("AAPL")

            assert result is not None
            assert result.symbol == "AAPL"
            assert result.price == 175.50
            assert result.pe_ratio == 28.5
            assert result.sector == "Technology"

    def test_get_fundamentals_cache(self, client, mock_ticker_info):
        """Test that caching works."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker

            result1 = client.get_fundamentals("AAPL")
            result2 = client.get_fundamentals("AAPL")

            assert mock_ticker_class.call_count == 1
            assert result1.symbol == result2.symbol

    def test_get_fundamentals_no_data(self, client):
        """Test handling of missing data."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = {}
            mock_ticker_class.return_value = mock_ticker

            result = client.get_fundamentals("INVALID")

            assert result is None

    def test_get_fundamentals_batch(self, client, mock_ticker_info):
        """Test batch fetching."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker

            results = client.get_fundamentals_batch(["AAPL", "MSFT"])

            assert len(results) == 2
            assert "AAPL" in results
            assert "MSFT" in results

    def test_clear_cache(self, client, mock_ticker_info):
        """Test cache clearing."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker

            client.get_fundamentals("AAPL")
            assert len(client._cache) == 1

            client.clear_cache()
            assert len(client._cache) == 0

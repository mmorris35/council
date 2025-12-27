"""
Pytest configuration and fixtures for Council tests.

File Name      : conftest.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_TABLE_PREFIX", "council-test")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("SES_SENDER_EMAIL", "test@example.com")


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "AAPL": {
            "price": 175.50,
            "pe_ratio": 28.5,
            "pb_ratio": 45.2,
            "market_cap": 2800000000000,
            "dividend_yield": 0.005,
            "current_ratio": 1.0,
            "debt_to_equity": 1.8,
        },
        "BRK-B": {
            "price": 365.00,
            "pe_ratio": 9.5,
            "pb_ratio": 1.4,
            "market_cap": 800000000000,
            "dividend_yield": 0.0,
            "current_ratio": 3.2,
            "debt_to_equity": 0.2,
        },
    }

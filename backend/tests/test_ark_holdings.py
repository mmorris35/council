"""
Tests for ARK Holdings client.

File Name      : test_ark_holdings.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from datetime import date
from src.data.ark_holdings import ARKHoldingsClient, ARKDailySnapshot, ARKHolding


class TestARKHoldingsClient:
    """Tests for ARKHoldingsClient."""

    @pytest.fixture
    def client(self):
        return ARKHoldingsClient()

    @pytest.fixture
    def sample_snapshot(self):
        return ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1000000, market_value=200000000, weight=0.10),
                ARKHolding(fund="ARKK", date=date.today(), company="Roku Inc", ticker="ROKU", cusip="77543R102", shares=500000, market_value=50000000, weight=0.05),
            ],
            total_value=250000000,
        )

    def test_compare_holdings_added(self, client, sample_snapshot):
        """Test detecting added positions."""
        previous = ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1000000, market_value=200000000, weight=0.10),
            ],
            total_value=200000000,
        )

        changes = client.compare_holdings(sample_snapshot, previous)

        assert len(changes["added"]) == 1
        assert changes["added"][0].ticker == "ROKU"

    def test_compare_holdings_increased(self, client):
        """Test detecting increased positions."""
        current = ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1100000, market_value=220000000, weight=0.11),
            ],
            total_value=220000000,
        )
        previous = ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1000000, market_value=200000000, weight=0.10),
            ],
            total_value=200000000,
        )

        changes = client.compare_holdings(current, previous)

        assert len(changes["increased"]) == 1

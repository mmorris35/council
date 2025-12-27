"""
Tests for SEC EDGAR client.

File Name      : test_sec_edgar.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from datetime import datetime
from src.data.sec_edgar import SECEdgarClient, Filing13F, Holding


class TestSECEdgarClient:
    """Tests for SECEdgarClient."""

    @pytest.fixture
    def client(self):
        return SECEdgarClient()

    @pytest.fixture
    def sample_filing(self):
        return Filing13F(
            cik="0001067983",
            company_name="Berkshire Hathaway",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
                Holding(name="BANK OF AMER", cusip="060505104", value=30000000, shares=1000000000, share_type="SH"),
            ],
            total_value=180000000,
        )

    def test_compare_holdings_added(self, client, sample_filing):
        """Test detecting added positions."""
        previous = Filing13F(
            cik="0001067983",
            company_name="Berkshire Hathaway",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
            ],
            total_value=150000000,
        )

        changes = client.compare_holdings(sample_filing, previous)

        assert len(changes["added"]) == 1
        assert changes["added"][0].name == "BANK OF AMER"
        assert len(changes["removed"]) == 0

    def test_compare_holdings_removed(self, client, sample_filing):
        """Test detecting removed positions."""
        previous = Filing13F(
            cik="0001067983",
            company_name="Berkshire Hathaway",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
                Holding(name="BANK OF AMER", cusip="060505104", value=30000000, shares=1000000000, share_type="SH"),
                Holding(name="COCA-COLA", cusip="191216100", value=25000000, shares=400000000, share_type="SH"),
            ],
            total_value=205000000,
        )

        changes = client.compare_holdings(sample_filing, previous)

        assert len(changes["removed"]) == 1
        assert changes["removed"][0].name == "COCA-COLA"

    def test_compare_holdings_increased(self, client):
        """Test detecting increased positions."""
        current = Filing13F(
            cik="0001067983",
            company_name="Test",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=200000000, shares=1200000000, share_type="SH"),
            ],
            total_value=200000000,
        )
        previous = Filing13F(
            cik="0001067983",
            company_name="Test",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
            ],
            total_value=150000000,
        )

        changes = client.compare_holdings(current, previous)

        assert len(changes["increased"]) == 1
        assert changes["increased"][0].shares == 1200000000

"""
Tests for Lynch agent.

File Name      : test_lynch_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.lynch import LynchAgent, StockCategory
from src.db.models import AgentType, Portfolio
from src.data.yfinance_client import StockFundamentals


class TestLynchAgent:
    """Tests for LynchAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        return MagicMock()

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return LynchAgent(db_client=mock_db, data_client=mock_data)

    def test_peg_calculation(self, agent):
        """Test PEG ratio calculation."""
        data = StockFundamentals(
            symbol="TEST",
            price=100.0,
            pe_ratio=20.0,
            earnings_growth=0.20,  # 20%
        )

        peg = agent._calculate_peg(data)

        assert peg == pytest.approx(1.0, rel=0.01)

    def test_classify_fast_grower(self, agent):
        """Test fast grower classification."""
        data = StockFundamentals(
            symbol="FAST",
            price=100.0,
            earnings_growth=0.25,  # 25%
        )

        category = agent._classify_stock(data)

        assert category == StockCategory.FAST_GROWER

    def test_classify_stalwart(self, agent):
        """Test stalwart classification."""
        data = StockFundamentals(
            symbol="STEADY",
            price=100.0,
            earnings_growth=0.12,  # 12%
        )

        category = agent._classify_stock(data)

        assert category == StockCategory.STALWART

    def test_classify_slow_grower(self, agent):
        """Test slow grower classification."""
        data = StockFundamentals(
            symbol="SLOW",
            price=100.0,
            earnings_growth=0.03,  # 3%
        )

        category = agent._classify_stock(data)

        assert category == StockCategory.SLOW_GROWER

    def test_no_peg_without_growth(self, agent):
        """Test PEG returns None without growth data."""
        data = StockFundamentals(
            symbol="NOGROW",
            price=100.0,
            pe_ratio=20.0,
            earnings_growth=None,
        )

        peg = agent._calculate_peg(data)

        assert peg is None

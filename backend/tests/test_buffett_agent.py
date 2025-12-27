"""
Tests for Buffett agent.

File Name      : test_buffett_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.buffett import BuffettAgent
from src.db.models import AgentType, Portfolio, Position
from src.data.yfinance_client import StockFundamentals


class TestBuffettAgent:
    """Tests for BuffettAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        return mock

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return BuffettAgent(db_client=mock_db, data_client=mock_data)

    @pytest.fixture
    def quality_stock(self):
        return StockFundamentals(
            symbol="AAPL",
            price=175.0,
            pe_ratio=28.0,
            pb_ratio=45.0,
            return_on_equity=0.25,
            profit_margin=0.25,
            debt_to_equity=80.0,
            current_ratio=1.5,
            market_cap=2800000000000,
        )

    @pytest.fixture
    def poor_stock(self):
        return StockFundamentals(
            symbol="BAD",
            price=10.0,
            pe_ratio=50.0,
            pb_ratio=5.0,
            return_on_equity=0.05,
            profit_margin=0.02,
            debt_to_equity=300.0,
            current_ratio=0.8,
            market_cap=1000000000,
        )

    def test_has_moat_quality_company(self, agent, quality_stock):
        """Test moat detection for quality company."""
        assert agent._has_moat(quality_stock) is True

    def test_has_moat_poor_company(self, agent, poor_stock):
        """Test moat detection for poor company."""
        assert agent._has_moat(poor_stock) is False

    def test_buffett_score_quality(self, agent, quality_stock):
        """Test scoring for quality company."""
        score = agent._calculate_buffett_score(quality_stock)
        assert score >= 0.6

    def test_buffett_score_poor(self, agent, poor_stock):
        """Test scoring for poor company."""
        score = agent._calculate_buffett_score(poor_stock)
        assert score < 0.5

    def test_position_sizing(self, agent, quality_stock):
        """Test position size calculation."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[],
        )

        shares = agent._calculate_position_size(portfolio, quality_stock)

        position_value = shares * quality_stock.price
        assert position_value <= portfolio.cash * 0.5
        assert position_value <= portfolio.total_value * 0.15

    def test_no_buy_overvalued(self, agent, mock_data):
        """Test no buy recommendation for overvalued stocks."""
        overvalued = StockFundamentals(
            symbol="OVER",
            price=500.0,
            pe_ratio=100.0,
            return_on_equity=0.20,
            profit_margin=0.15,
            debt_to_equity=50.0,
        )

        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[],
        )

        assert agent._is_buy_candidate(overvalued, portfolio) is False

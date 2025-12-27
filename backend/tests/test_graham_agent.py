"""
Tests for Graham agent.

File Name      : test_graham_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.graham import GrahamAgent
from src.db.models import AgentType, Portfolio, Position
from src.data.yfinance_client import StockFundamentals


class TestGrahamAgent:
    """Tests for GrahamAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        return MagicMock()

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return GrahamAgent(db_client=mock_db, data_client=mock_data)

    @pytest.fixture
    def graham_stock(self):
        """Stock that passes Graham screen."""
        return StockFundamentals(
            symbol="VALUE",
            price=50.0,
            pe_ratio=10.0,
            pb_ratio=1.2,
            current_ratio=2.5,
            debt_to_equity=30.0,
            earnings_growth=0.05,
        )

    @pytest.fixture
    def growth_stock(self):
        """Stock that fails Graham screen."""
        return StockFundamentals(
            symbol="GROWTH",
            price=500.0,
            pe_ratio=50.0,
            pb_ratio=15.0,
            current_ratio=1.2,
            debt_to_equity=150.0,
        )

    def test_passes_graham_screen_value(self, agent, graham_stock):
        """Test screen passes for value stock."""
        assert agent._passes_graham_screen(graham_stock) is True

    def test_fails_graham_screen_growth(self, agent, growth_stock):
        """Test screen fails for growth stock."""
        assert agent._passes_graham_screen(growth_stock) is False

    def test_intrinsic_value_calculation(self, agent, graham_stock):
        """Test intrinsic value calculation."""
        intrinsic = agent._calculate_intrinsic_value(graham_stock)

        eps = 50.0 / 10.0  # $5
        expected = eps * (8.5 + 2 * 5.0)  # g=5%

        assert intrinsic == pytest.approx(expected, rel=0.01)

    def test_margin_of_safety(self, agent, graham_stock):
        """Test margin of safety calculation."""
        intrinsic = 100.0
        graham_stock.price = 60.0

        margin = agent._calculate_margin_of_safety(graham_stock, intrinsic)

        assert margin == pytest.approx(0.4, rel=0.01)

    def test_position_size_respects_max(self, agent, graham_stock):
        """Test position sizing respects 5% max."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.GRAHAM,
            cash=100000.0,
            positions=[],
        )

        shares = agent._calculate_position_size(portfolio, graham_stock)
        position_value = shares * graham_stock.price

        assert position_value <= portfolio.total_value * 0.05 + graham_stock.price

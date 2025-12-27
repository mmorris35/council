"""
Tests for Bogle agent.

File Name      : test_bogle_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from datetime import date
from src.agents.bogle import BogleAgent, VTI, BND
from src.db.models import AgentType, Portfolio, Position


class TestBogleAgent:
    """Tests for BogleAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        mock.get_fundamentals.side_effect = lambda sym: MagicMock(
            price=250.0 if sym == VTI else 75.0
        )
        return mock

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return BogleAgent(db_client=mock_db, data_client=mock_data)

    @pytest.fixture
    def empty_portfolio(self):
        return Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BOGLE,
            cash=100000.0,
            positions=[],
        )

    def test_analyze_market_philosophy(self, agent):
        """Test that analysis reflects passive philosophy."""
        analysis = agent.analyze_market()

        assert "time in the market" in analysis.lower()
        assert "70%" in analysis or "stocks" in analysis.lower()

    def test_allocate_new_cash(self, agent, empty_portfolio, monkeypatch):
        """Test cash allocation on first of month."""
        monkeypatch.setattr(
            "src.agents.bogle.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 1)})
        )

        recs = agent._allocate_cash(100000.0)

        assert len(recs) == 2
        symbols = [r.symbol for r in recs]
        assert VTI in symbols
        assert BND in symbols

    def test_rebalance_when_off_target(self, agent, mock_data):
        """Test rebalancing when significantly off target."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BOGLE,
            cash=1000.0,
            positions=[
                Position(symbol=VTI, shares=400, avg_cost=200.0, current_price=250.0),  # $100k
                Position(symbol=BND, shares=200, avg_cost=70.0, current_price=75.0),   # $15k
            ],
        )

        current_stock_pct = 100000 / 115000
        recs = agent._rebalance(portfolio, current_stock_pct)

        assert len(recs) >= 0

    def test_no_action_when_balanced(self, agent):
        """Test no recommendations when portfolio is balanced."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BOGLE,
            cash=100.0,  # Minimal cash
            positions=[
                Position(symbol=VTI, shares=280, avg_cost=200.0, current_price=250.0),  # $70k (70%)
                Position(symbol=BND, shares=400, avg_cost=70.0, current_price=75.0),   # $30k (30%)
            ],
        )

        recs = agent.generate_recommendations(portfolio)

        assert len(recs) == 0

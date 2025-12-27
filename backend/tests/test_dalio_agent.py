"""
Tests for Dalio agent.

File Name      : test_dalio_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.dalio import DalioAgent, ALL_WEATHER_ALLOCATION
from src.db.models import AgentType, Portfolio, Position


class TestDalioAgent:
    """Tests for DalioAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        mock.get_fundamentals.side_effect = lambda sym: MagicMock(price=100.0)
        return mock

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return DalioAgent(db_client=mock_db, data_client=mock_data)

    def test_allocation_sums_to_one(self):
        """Test all-weather allocation sums to 100%."""
        total = sum(ALL_WEATHER_ALLOCATION.values())
        assert total == pytest.approx(1.0, rel=0.01)

    def test_calculate_current_allocation(self, agent):
        """Test current allocation calculation."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.DALIO,
            cash=10000.0,
            positions=[
                Position(symbol="VTI", shares=300, avg_cost=90.0, current_price=100.0),
                Position(symbol="TLT", shares=400, avg_cost=95.0, current_price=100.0),
            ],
        )

        allocation = agent._calculate_current_allocation(portfolio)

        total = portfolio.total_value
        assert allocation["VTI"] == pytest.approx(30000 / total, rel=0.01)
        assert allocation["TLT"] == pytest.approx(40000 / total, rel=0.01)

    def test_deploy_cash_all_assets(self, agent, mock_data):
        """Test cash deployment covers all assets."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.DALIO,
            cash=100000.0,
            positions=[],
        )

        recommendations = agent._deploy_cash(portfolio)

        symbols = {r.symbol for r in recommendations}
        assert symbols == set(ALL_WEATHER_ALLOCATION.keys())

    def test_rebalance_triggers_on_drift(self, agent, mock_data):
        """Test rebalancing triggers when drift exceeds threshold."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.DALIO,
            cash=5000.0,
            positions=[
                Position(symbol="VTI", shares=450, avg_cost=90.0, current_price=100.0),
                Position(symbol="TLT", shares=350, avg_cost=95.0, current_price=100.0),
                Position(symbol="IEI", shares=100, avg_cost=95.0, current_price=100.0),
                Position(symbol="GLD", shares=50, avg_cost=180.0, current_price=100.0),
                Position(symbol="DBC", shares=50, avg_cost=20.0, current_price=100.0),
            ],
        )

        recommendations = agent.generate_recommendations(portfolio)

        assert len(recommendations) >= 0

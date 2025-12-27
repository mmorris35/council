"""
Tests for base agent class.

File Name      : test_base_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock, patch
from src.agents.base import BaseAgent, TradeRecommendation
from src.db.models import AgentType, TransactionType, Portfolio, Position


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""
    agent_type = AgentType.BUFFETT
    agent_name = "Test Agent"
    description = "Test agent implementation"

    def analyze_market(self) -> str:
        return "Market looks good"

    def generate_recommendations(self, portfolio: Portfolio):
        return [
            TradeRecommendation(
                action=TransactionType.BUY,
                symbol="AAPL",
                shares=10,
                reasoning="Test buy",
                confidence=0.8,
            )
        ]


class TestBaseAgent:
    """Tests for BaseAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        mock.get_fundamentals.return_value = MagicMock(price=175.0)
        return mock

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return ConcreteAgent(db_client=mock_db, data_client=mock_data)

    @pytest.fixture
    def sample_portfolio(self):
        return Portfolio(
            portfolio_id="test-port",
            user_id="test-user",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[],
        )

    def test_execute_buy_trade(self, agent, mock_db, mock_data, sample_portfolio):
        """Test executing a buy trade."""
        recommendation = TradeRecommendation(
            action=TransactionType.BUY,
            symbol="AAPL",
            shares=10,
            reasoning="Test buy",
            confidence=0.8,
        )

        txn = agent._execute_trade(sample_portfolio, recommendation)

        assert txn is not None
        assert txn.symbol == "AAPL"
        assert txn.shares == 10
        assert sample_portfolio.cash == 100000 - (175 * 10)
        assert len(sample_portfolio.positions) == 1

    def test_execute_sell_trade(self, agent, mock_db, mock_data, sample_portfolio):
        """Test executing a sell trade."""
        sample_portfolio.positions.append(
            Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
        )

        recommendation = TradeRecommendation(
            action=TransactionType.SELL,
            symbol="AAPL",
            shares=50,
            reasoning="Test sell",
            confidence=0.9,
        )

        txn = agent._execute_trade(sample_portfolio, recommendation)

        assert txn is not None
        assert sample_portfolio.positions[0].shares == 50
        assert sample_portfolio.cash == 100000 + (175 * 50)

    def test_insufficient_cash(self, agent, mock_db, mock_data, sample_portfolio):
        """Test handling insufficient cash for buy."""
        sample_portfolio.cash = 100  # Very low

        recommendation = TradeRecommendation(
            action=TransactionType.BUY,
            symbol="AAPL",
            shares=1000,
            reasoning="Test buy",
            confidence=0.8,
        )

        txn = agent._execute_trade(sample_portfolio, recommendation)

        # Should buy what we can afford (0 shares at $175)
        assert txn is None

"""
Tests for Wood agent.

File Name      : test_wood_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.wood import WoodAgent, InnovationTheme, THEME_STOCKS
from src.db.models import AgentType, Portfolio, Position
from src.data.yfinance_client import StockFundamentals


class TestWoodAgent:
    """Tests for WoodAgent."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_data(self):
        return MagicMock()

    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return WoodAgent(db_client=mock_db, data_client=mock_data)

    def test_themes_have_stocks(self):
        """Test all themes have stocks assigned."""
        for theme in InnovationTheme:
            assert theme in THEME_STOCKS
            assert len(THEME_STOCKS[theme]) > 0

    def test_innovation_score_high_growth(self, agent):
        """Test high score for high growth stock."""
        data = StockFundamentals(
            symbol="GROWTH",
            price=100.0,
            revenue_growth=0.40,
            market_cap=5_000_000_000,
            beta=1.8,
        )

        score = agent._calculate_innovation_score(data)

        assert score > 0.7

    def test_innovation_score_low_growth(self, agent):
        """Test low score for low growth stock."""
        data = StockFundamentals(
            symbol="SLOW",
            price=100.0,
            revenue_growth=0.02,
            market_cap=500_000_000_000,
            beta=0.8,
        )

        score = agent._calculate_innovation_score(data)

        assert score < 0.5

    def test_get_stock_themes(self, agent):
        """Test getting themes for a stock."""
        themes = agent._get_stock_themes("TSLA")

        assert InnovationTheme.ENERGY in themes or InnovationTheme.MOBILITY in themes

    def test_buy_the_dip_detection(self, agent):
        """Test buy-the-dip detection."""
        data = StockFundamentals(
            symbol="DIP",
            price=70.0,
            fifty_two_week_high=120.0,
        )

        position = Position(
            symbol="DIP",
            shares=100,
            avg_cost=100.0,
            current_price=70.0,
        )

        assert agent._is_buy_the_dip(data, position) is True

"""
Cathie Wood Agent - Disruptive Innovation.

File Name      : wood.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL

Strategy:
- Focus on disruptive innovation themes
- High conviction, concentrated positions
- Long time horizon (5+ years)
- Buy the dip on high-growth names
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum

from .base import BaseAgent, TradeRecommendation
from src.db import Portfolio
from src.db.models import AgentType, TransactionType
from src.data.yfinance_client import StockFundamentals
from src.utils import get_logger

logger = get_logger(__name__)


class InnovationTheme(str, Enum):
    """ARK's innovation themes."""
    AI = "artificial_intelligence"
    ROBOTICS = "robotics_automation"
    ENERGY = "energy_storage"
    GENOMICS = "genomics"
    BLOCKCHAIN = "blockchain"
    MOBILITY = "autonomous_mobility"


THEME_STOCKS = {
    InnovationTheme.AI: ["NVDA", "MSFT", "GOOGL", "PLTR", "PATH", "SNOW"],
    InnovationTheme.ROBOTICS: ["ISRG", "ABB", "ROK", "TER", "FANUY"],
    InnovationTheme.ENERGY: ["TSLA", "ENPH", "SEDG", "RUN", "PLUG"],
    InnovationTheme.GENOMICS: ["CRSP", "BEAM", "NTLA", "EDIT", "PACB"],
    InnovationTheme.BLOCKCHAIN: ["COIN", "SQ", "MSTR", "RIOT", "MARA"],
    InnovationTheme.MOBILITY: ["TSLA", "UBER", "LYFT", "APTV", "LAZR"],
}


class WoodAgent(BaseAgent):
    """
    Cathie Wood's disruptive innovation philosophy.

    "We are on the right side of change."

    Strategy:
    - Focus on 5-year time horizons
    - Invest in innovation platforms
    - High conviction, concentrated positions
    - Use volatility to add to positions
    """

    agent_type = AgentType.WOOD
    agent_name = "Cathie Wood"
    description = "Disruptive innovation - invest in the future"

    MAX_POSITIONS = 35
    TOP_POSITION_PCT = 0.10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze_market(self) -> str:
        """Analyze innovation themes."""
        today = datetime.now()

        theme_analysis = []
        for theme in InnovationTheme:
            stocks = THEME_STOCKS.get(theme, [])[:3]
            theme_data = []
            for symbol in stocks:
                data = self.data.get_fundamentals(symbol)
                if data:
                    theme_data.append((symbol, data))
            theme_analysis.append((theme, theme_data))

        analysis = (
            f"Date: {today.date().isoformat()}\n"
            f"Philosophy: We are on the right side of change.\n\n"
            f"Innovation Themes Analysis:\n"
        )

        for theme, stocks in theme_analysis:
            analysis += f"\n{theme.value.replace('_', ' ').title()}:\n"
            for symbol, data in stocks[:2]:
                growth = (data.revenue_growth or 0) * 100
                analysis += f"  - {symbol}: Revenue growth {growth:.0f}%\n"

        analysis += (
            f"\n5-Year Vision:\n"
            f"- AI will transform every industry\n"
            f"- Electric vehicles will dominate\n"
            f"- Genomics will revolutionize healthcare\n"
            f"- Bitcoin will become digital gold\n\n"
            f"Wisdom: 'Innovation solves problems. The bigger the problem, "
            f"the bigger the opportunity.'"
        )

        return analysis

    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """Generate recommendations based on innovation themes."""
        recommendations = []

        current_symbols = {p.symbol for p in portfolio.positions}

        all_theme_stocks = set()
        for stocks in THEME_STOCKS.values():
            all_theme_stocks.update(stocks)

        candidates = []
        for symbol in all_theme_stocks:
            if symbol in current_symbols:
                continue

            data = self.data.get_fundamentals(symbol)
            if not data:
                continue

            score = self._calculate_innovation_score(data)
            if score > 0.5:
                themes = self._get_stock_themes(symbol)
                candidates.append((symbol, score, themes, data))

        candidates.sort(key=lambda x: x[1], reverse=True)

        for symbol, score, themes, data in candidates[:3]:
            shares = self._calculate_position_size(portfolio, data, score)
            if shares > 0:
                recommendations.append(TradeRecommendation(
                    action=TransactionType.BUY,
                    symbol=symbol,
                    shares=shares,
                    reasoning=f"Innovation play ({', '.join(t.value for t in themes)}), score {score:.2f}",
                    confidence=min(0.9, score),
                ))

        for position in portfolio.positions:
            data = self.data.get_fundamentals(position.symbol)
            if data and self._is_buy_the_dip(data, position):
                shares = self._calculate_position_size(portfolio, data, 0.7)
                if shares > 0:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.BUY,
                        symbol=position.symbol,
                        shares=shares,
                        reasoning="Adding on weakness - conviction unchanged",
                        confidence=0.75,
                    ))

        return recommendations

    def _calculate_innovation_score(self, data: StockFundamentals) -> float:
        """Calculate innovation/growth score."""
        score = 0.0
        factors = 0

        if data.revenue_growth:
            if data.revenue_growth > 0.30:
                score += 1.0
            elif data.revenue_growth > 0.20:
                score += 0.8
            elif data.revenue_growth > 0.10:
                score += 0.5
            factors += 1

        if data.market_cap:
            if data.market_cap < 10_000_000_000:
                score += 0.8
            elif data.market_cap < 50_000_000_000:
                score += 0.6
            else:
                score += 0.3
            factors += 1

        if data.beta:
            if data.beta > 1.5:
                score += 0.7
            elif data.beta > 1.2:
                score += 0.5
            factors += 1

        return score / max(factors, 1)

    def _get_stock_themes(self, symbol: str) -> List[InnovationTheme]:
        """Get innovation themes for a stock."""
        themes = []
        for theme, stocks in THEME_STOCKS.items():
            if symbol in stocks:
                themes.append(theme)
        return themes

    def _is_buy_the_dip(self, data: StockFundamentals, position) -> bool:
        """Check if we should add on weakness."""
        if not data.fifty_two_week_high or not data.price:
            return False

        drawdown = (data.fifty_two_week_high - data.price) / data.fifty_two_week_high

        return drawdown > 0.30 and position.gain_loss_pct < -0.20

    def _calculate_position_size(
        self,
        portfolio: Portfolio,
        data: StockFundamentals,
        score: float
    ) -> int:
        """Calculate position size based on conviction."""
        base_pct = 0.03 + (score * 0.04)
        max_position_value = portfolio.total_value * min(base_pct, self.TOP_POSITION_PCT)
        available_cash = portfolio.cash * 0.3

        position_value = min(max_position_value, available_cash)

        if data.price and data.price > 0:
            return int(position_value / data.price)

        return 0

"""
Warren Buffett Agent - Value Investing with Moats.

File Name      : buffett.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL

Strategy:
- Buy wonderful companies at fair prices
- Look for durable competitive advantages (moats)
- Concentrated portfolio, hold forever
- Wait for "blood in the streets" opportunities
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from .base import BaseAgent, TradeRecommendation
from src.db import Portfolio
from src.db.models import AgentType, TransactionType
from src.data.yfinance_client import StockFundamentals
from src.utils import get_logger

logger = get_logger(__name__)

BUFFETT_WATCHLIST = [
    "AAPL", "KO", "AXP", "BAC", "CVX", "OXY", "KHC", "MCO", "DVA", "VRSN",
    "V", "MA", "JNJ", "PG", "WMT", "COST", "HD", "UNH", "JPM", "BRK-B"
]


class BuffettAgent(BaseAgent):
    """
    Warren Buffett's value investing philosophy.

    "It's far better to buy a wonderful company at a fair price
    than a fair company at a wonderful price."

    Strategy:
    - Seek companies with durable competitive advantages
    - Focus on return on equity, profit margins, debt levels
    - Prefer predictable earnings and strong brands
    - Hold concentrated positions in high-conviction ideas
    - Be greedy when others are fearful
    """

    agent_type = AgentType.BUFFETT
    agent_name = "Warren Buffett"
    description = "Value investing - wonderful companies at fair prices"

    def __init__(self, max_positions: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.max_positions = max_positions
        self.min_conviction = 0.75

    def analyze_market(self) -> str:
        """Analyze market for value opportunities."""
        today = datetime.now()

        opportunities = []
        for symbol in BUFFETT_WATCHLIST[:10]:
            data = self.data.get_fundamentals(symbol)
            if data and self._has_moat(data):
                score = self._calculate_buffett_score(data)
                if score >= 0.6:
                    opportunities.append((symbol, score, data))

        opportunities.sort(key=lambda x: x[1], reverse=True)

        analysis = (
            f"Date: {today.date().isoformat()}\n"
            f"Philosophy: Buy wonderful companies at fair prices.\n\n"
            f"Market Scan Results:\n"
        )

        for symbol, score, data in opportunities[:5]:
            analysis += (
                f"- {symbol}: Score {score:.2f}, "
                f"P/E {data.pe_ratio or 'N/A'}, "
                f"ROE {data.return_on_equity*100 if data.return_on_equity else 'N/A'}%\n"
            )

        if not opportunities:
            analysis += "No compelling opportunities today. Cash is a position.\n"

        analysis += (
            f"\nWisdom: 'The stock market is designed to transfer money "
            f"from the Active to the Patient.'"
        )

        return analysis

    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """Generate recommendations based on value criteria."""
        recommendations = []

        current_symbols = {p.symbol for p in portfolio.positions}

        for position in portfolio.positions:
            data = self.data.get_fundamentals(position.symbol)
            if data and self._should_sell(data, position):
                recommendations.append(TradeRecommendation(
                    action=TransactionType.SELL,
                    symbol=position.symbol,
                    shares=position.shares,
                    reasoning=f"Moat deterioration or extreme overvaluation",
                    confidence=0.8,
                ))

        if len(current_symbols) < self.max_positions:
            for symbol in BUFFETT_WATCHLIST:
                if symbol in current_symbols:
                    continue

                data = self.data.get_fundamentals(symbol)
                if not data:
                    continue

                if self._is_buy_candidate(data, portfolio):
                    score = self._calculate_buffett_score(data)
                    position_size = self._calculate_position_size(portfolio, data)

                    if position_size > 0:
                        recommendations.append(TradeRecommendation(
                            action=TransactionType.BUY,
                            symbol=symbol,
                            shares=position_size,
                            reasoning=self._generate_buy_reasoning(data, score),
                            confidence=min(0.95, score),
                        ))

                if len(recommendations) >= 2:
                    break

        return recommendations

    def _has_moat(self, data: StockFundamentals) -> bool:
        """Check if company has a durable competitive advantage."""
        moat_signals = 0

        if data.return_on_equity and data.return_on_equity > 0.15:
            moat_signals += 1

        if data.profit_margin and data.profit_margin > 0.10:
            moat_signals += 1

        if data.debt_to_equity is not None and data.debt_to_equity < 100:
            moat_signals += 1

        if data.revenue_growth and data.revenue_growth > 0:
            moat_signals += 1

        return moat_signals >= 2

    def _calculate_buffett_score(self, data: StockFundamentals) -> float:
        """Calculate a Buffett-style quality score (0-1)."""
        score = 0.0
        factors = 0

        if data.pe_ratio:
            if data.pe_ratio < 15:
                score += 1.0
            elif data.pe_ratio < 20:
                score += 0.7
            elif data.pe_ratio < 25:
                score += 0.4
            else:
                score += 0.1
            factors += 1

        if data.return_on_equity:
            if data.return_on_equity > 0.20:
                score += 1.0
            elif data.return_on_equity > 0.15:
                score += 0.7
            elif data.return_on_equity > 0.10:
                score += 0.4
            factors += 1

        if data.profit_margin:
            if data.profit_margin > 0.20:
                score += 1.0
            elif data.profit_margin > 0.10:
                score += 0.6
            factors += 1

        if data.debt_to_equity is not None:
            if data.debt_to_equity < 50:
                score += 1.0
            elif data.debt_to_equity < 100:
                score += 0.6
            elif data.debt_to_equity < 200:
                score += 0.3
            factors += 1

        if data.current_ratio:
            if data.current_ratio > 1.5:
                score += 0.8
            elif data.current_ratio > 1.0:
                score += 0.5
            factors += 1

        return score / max(factors, 1)

    def _is_buy_candidate(self, data: StockFundamentals, portfolio: Portfolio) -> bool:
        """Determine if stock is a buy candidate."""
        if not self._has_moat(data):
            return False

        score = self._calculate_buffett_score(data)
        if score < 0.6:
            return False

        if data.pe_ratio and data.pe_ratio > 30:
            return False

        return True

    def _should_sell(self, data: StockFundamentals, position) -> bool:
        """Determine if we should sell a position."""
        if not self._has_moat(data):
            return True

        if data.pe_ratio and data.pe_ratio > 50:
            return True

        return False

    def _calculate_position_size(
        self,
        portfolio: Portfolio,
        data: StockFundamentals
    ) -> int:
        """Calculate appropriate position size."""
        max_position_value = portfolio.total_value * 0.15
        available_cash = portfolio.cash * 0.5

        position_value = min(max_position_value, available_cash)

        if data.price and data.price > 0:
            shares = int(position_value / data.price)
            return max(0, shares)

        return 0

    def _generate_buy_reasoning(self, data: StockFundamentals, score: float) -> str:
        """Generate reasoning for buy recommendation."""
        reasons = []

        if data.return_on_equity and data.return_on_equity > 0.15:
            reasons.append(f"Strong ROE of {data.return_on_equity*100:.1f}%")

        if data.profit_margin and data.profit_margin > 0.10:
            reasons.append(f"Healthy margins of {data.profit_margin*100:.1f}%")

        if data.pe_ratio and data.pe_ratio < 20:
            reasons.append(f"Reasonable P/E of {data.pe_ratio:.1f}")

        if data.debt_to_equity is not None and data.debt_to_equity < 100:
            reasons.append("Conservative debt levels")

        return f"Quality score {score:.2f}. " + "; ".join(reasons) if reasons else f"Buffett score: {score:.2f}"

"""
Benjamin Graham Agent - Deep Value Investing.

File Name      : graham.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL

Strategy:
- Strict quantitative screens
- Margin of safety is paramount
- Diversify across many positions
- Buy below intrinsic value
"""
from datetime import datetime
from typing import List, Optional

from .base import BaseAgent, TradeRecommendation
from src.db import Portfolio
from src.db.models import AgentType, TransactionType
from src.data.yfinance_client import StockFundamentals
from src.utils import get_logger

logger = get_logger(__name__)


class GrahamAgent(BaseAgent):
    """
    Benjamin Graham's deep value investing philosophy.

    "The intelligent investor is a realist who sells to optimists
    and buys from pessimists."

    Strategy:
    - P/E ratio < 15 (ideally < 10)
    - P/B ratio < 1.5 (ideally < 1.0)
    - Current ratio > 2.0
    - Debt to equity < 0.5
    - Positive earnings for 10 years
    - Dividend history
    - Diversify across 20-30 positions
    """

    agent_type = AgentType.GRAHAM
    agent_name = "Benjamin Graham"
    description = "Deep value investing - buy cigar butts with margin of safety"

    # Graham's criteria
    MAX_PE = 15
    MAX_PB = 1.5
    MIN_CURRENT_RATIO = 2.0
    MAX_DEBT_EQUITY = 50  # 0.5 as percentage
    MIN_POSITIONS = 20
    MAX_POSITIONS = 30
    MAX_POSITION_PCT = 0.05  # 5% max per position

    def analyze_market(self) -> str:
        """Screen market for Graham-style bargains."""
        today = datetime.now()

        sp500 = self.data.get_sp500_symbols()[:100]

        bargains = []
        for symbol in sp500:
            data = self.data.get_fundamentals(symbol)
            if data and self._passes_graham_screen(data):
                intrinsic = self._calculate_intrinsic_value(data)
                margin = self._calculate_margin_of_safety(data, intrinsic)
                if margin > 0.2:
                    bargains.append((symbol, margin, data))

        bargains.sort(key=lambda x: x[1], reverse=True)

        analysis = (
            f"Date: {today.date().isoformat()}\n"
            f"Philosophy: Buy $1 bills for $0.50.\n\n"
            f"Screening {len(sp500)} stocks against Graham criteria:\n"
            f"- P/E < {self.MAX_PE}\n"
            f"- P/B < {self.MAX_PB}\n"
            f"- Current Ratio > {self.MIN_CURRENT_RATIO}\n"
            f"- Debt/Equity < {self.MAX_DEBT_EQUITY}%\n\n"
            f"Bargains Found: {len(bargains)}\n"
        )

        for symbol, margin, data in bargains[:5]:
            analysis += (
                f"- {symbol}: {margin*100:.0f}% margin of safety, "
                f"P/E {data.pe_ratio:.1f}, P/B {data.pb_ratio:.2f}\n"
            )

        analysis += (
            f"\nWisdom: 'In the short run, the market is a voting machine "
            f"but in the long run, it is a weighing machine.'"
        )

        return analysis

    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """Generate recommendations based on Graham criteria."""
        recommendations = []

        current_symbols = {p.symbol for p in portfolio.positions}

        for position in portfolio.positions:
            data = self.data.get_fundamentals(position.symbol)
            if data:
                if not self._passes_graham_screen(data):
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.SELL,
                        symbol=position.symbol,
                        shares=position.shares,
                        reasoning="No longer meets Graham criteria",
                        confidence=0.75,
                    ))
                elif data.pe_ratio and data.pe_ratio > 20:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.SELL,
                        symbol=position.symbol,
                        shares=position.shares,
                        reasoning=f"P/E expanded to {data.pe_ratio:.1f}, take profits",
                        confidence=0.7,
                    ))

        if len(current_symbols) < self.MIN_POSITIONS:
            sp500 = self.data.get_sp500_symbols()[:200]

            candidates = []
            for symbol in sp500:
                if symbol in current_symbols:
                    continue

                data = self.data.get_fundamentals(symbol)
                if data and self._passes_graham_screen(data):
                    intrinsic = self._calculate_intrinsic_value(data)
                    margin = self._calculate_margin_of_safety(data, intrinsic)
                    if margin > 0.25:
                        candidates.append((symbol, margin, data))

            candidates.sort(key=lambda x: x[1], reverse=True)

            for symbol, margin, data in candidates[:3]:
                shares = self._calculate_position_size(portfolio, data)
                if shares > 0:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.BUY,
                        symbol=symbol,
                        shares=shares,
                        reasoning=f"Graham bargain: {margin*100:.0f}% margin of safety",
                        confidence=min(0.9, 0.5 + margin),
                    ))

        return recommendations

    def _passes_graham_screen(self, data: StockFundamentals) -> bool:
        """Check if stock passes Graham's quantitative screen."""
        if data.pe_ratio is None or data.pe_ratio > self.MAX_PE:
            return False

        if data.pe_ratio <= 0:
            return False

        if data.pb_ratio is None or data.pb_ratio > self.MAX_PB:
            return False

        if data.current_ratio is None or data.current_ratio < self.MIN_CURRENT_RATIO:
            return False

        if data.debt_to_equity is None or data.debt_to_equity > self.MAX_DEBT_EQUITY:
            return False

        return True

    def _calculate_intrinsic_value(self, data: StockFundamentals) -> float:
        """
        Calculate intrinsic value using Graham's formula.

        V = EPS x (8.5 + 2g)
        Where g = expected growth rate
        """
        if not data.price or not data.pe_ratio or data.pe_ratio <= 0:
            return 0.0

        eps = data.price / data.pe_ratio

        growth_rate = 5.0
        if data.earnings_growth:
            growth_rate = min(15, max(0, data.earnings_growth * 100))

        intrinsic = eps * (8.5 + 2 * growth_rate)

        return intrinsic

    def _calculate_margin_of_safety(
        self,
        data: StockFundamentals,
        intrinsic_value: float
    ) -> float:
        """Calculate margin of safety as percentage."""
        if intrinsic_value <= 0 or not data.price:
            return 0.0

        margin = (intrinsic_value - data.price) / intrinsic_value
        return max(0, margin)

    def _calculate_position_size(
        self,
        portfolio: Portfolio,
        data: StockFundamentals
    ) -> int:
        """Calculate position size respecting diversification."""
        max_position_value = portfolio.total_value * self.MAX_POSITION_PCT

        available_cash = portfolio.cash * 0.8

        position_value = min(max_position_value, available_cash)

        if data.price and data.price > 0:
            return int(position_value / data.price)

        return 0

"""
Peter Lynch Agent - GARP Investing.

File Name      : lynch.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL

Strategy:
- Invest in what you know
- PEG ratio < 1 is ideal
- Classify stocks: slow growers, stalwarts, fast growers, cyclicals, turnarounds, asset plays
- Look for ten-baggers
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


class StockCategory(str, Enum):
    """Lynch's stock classifications."""
    SLOW_GROWER = "slow_grower"
    STALWART = "stalwart"
    FAST_GROWER = "fast_grower"
    CYCLICAL = "cyclical"
    TURNAROUND = "turnaround"
    ASSET_PLAY = "asset_play"


LYNCH_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "HD", "NKE",
    "SBUX", "MCD", "DIS", "TGT", "COST", "WMT", "LULU", "CMG", "NFLX",
    "CRM", "ADBE", "NOW", "SHOP", "SQ", "PYPL", "V", "MA", "AXP"
]


class LynchAgent(BaseAgent):
    """
    Peter Lynch's GARP investing philosophy.

    "Know what you own, and know why you own it."

    Strategy:
    - PEG ratio (P/E divided by growth rate) < 1 is ideal
    - Invest in companies you understand
    - Classify stocks to set expectations
    - Look for fast growers with room to run
    - Avoid "diworsification"
    """

    agent_type = AgentType.LYNCH
    agent_name = "Peter Lynch"
    description = "Growth at reasonable price - invest in what you know"

    MAX_PEG = 1.5
    IDEAL_PEG = 1.0
    MAX_POSITIONS = 15

    def analyze_market(self) -> str:
        """Analyze market for growth opportunities."""
        today = datetime.now()

        categorized = {cat: [] for cat in StockCategory}

        for symbol in LYNCH_WATCHLIST:
            data = self.data.get_fundamentals(symbol)
            if data:
                category = self._classify_stock(data)
                peg = self._calculate_peg(data)
                if peg and peg > 0:
                    categorized[category].append((symbol, peg, data))

        analysis = (
            f"Date: {today.date().isoformat()}\n"
            f"Philosophy: Invest in what you know. PEG < 1 is a bargain.\n\n"
            f"Stock Classifications:\n"
        )

        for category in [StockCategory.FAST_GROWER, StockCategory.STALWART]:
            stocks = categorized[category]
            stocks.sort(key=lambda x: x[1])
            analysis += f"\n{category.value.replace('_', ' ').title()}:\n"
            for symbol, peg, data in stocks[:3]:
                analysis += f"  - {symbol}: PEG {peg:.2f}, Growth {(data.earnings_growth or 0)*100:.0f}%\n"

        analysis += (
            f"\nWisdom: 'Go for a business that any idiot can run - "
            f"because sooner or later, any idiot probably is going to run it.'"
        )

        return analysis

    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """Generate recommendations based on PEG and classification."""
        recommendations = []

        current_symbols = {p.symbol for p in portfolio.positions}

        for position in portfolio.positions:
            data = self.data.get_fundamentals(position.symbol)
            if data:
                peg = self._calculate_peg(data)
                if peg and peg > 2.5:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.SELL,
                        symbol=position.symbol,
                        shares=position.shares,
                        reasoning=f"PEG expanded to {peg:.2f}, overvalued",
                        confidence=0.75,
                    ))

        if len(current_symbols) < self.MAX_POSITIONS:
            candidates = []
            for symbol in LYNCH_WATCHLIST:
                if symbol in current_symbols:
                    continue

                data = self.data.get_fundamentals(symbol)
                if not data:
                    continue

                peg = self._calculate_peg(data)
                category = self._classify_stock(data)

                if peg and peg < self.MAX_PEG and category in [
                    StockCategory.FAST_GROWER, StockCategory.STALWART
                ]:
                    candidates.append((symbol, peg, category, data))

            candidates.sort(key=lambda x: x[1])

            for symbol, peg, category, data in candidates[:2]:
                shares = self._calculate_position_size(portfolio, data)
                if shares > 0:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.BUY,
                        symbol=symbol,
                        shares=shares,
                        reasoning=f"{category.value}: PEG {peg:.2f}",
                        confidence=min(0.9, 1.0 - peg/2),
                    ))

        return recommendations

    def _calculate_peg(self, data: StockFundamentals) -> Optional[float]:
        """Calculate PEG ratio."""
        if not data.pe_ratio or data.pe_ratio <= 0:
            return None

        if data.peg_ratio:
            return data.peg_ratio

        growth = data.earnings_growth
        if not growth or growth <= 0:
            return None

        growth_pct = growth * 100
        return data.pe_ratio / growth_pct

    def _classify_stock(self, data: StockFundamentals) -> StockCategory:
        """Classify stock using Lynch's categories."""
        growth = (data.earnings_growth or 0) * 100

        if growth > 20:
            return StockCategory.FAST_GROWER
        elif growth > 10:
            return StockCategory.STALWART
        elif growth > 0:
            return StockCategory.SLOW_GROWER
        elif growth < -10:
            return StockCategory.TURNAROUND

        if data.pb_ratio and data.pb_ratio < 1.0:
            return StockCategory.ASSET_PLAY

        if data.sector in ["Energy", "Materials", "Industrials"]:
            return StockCategory.CYCLICAL

        return StockCategory.STALWART

    def _calculate_position_size(
        self,
        portfolio: Portfolio,
        data: StockFundamentals
    ) -> int:
        """Calculate position size."""
        max_position_value = portfolio.total_value * 0.10
        available_cash = portfolio.cash * 0.4

        position_value = min(max_position_value, available_cash)

        if data.price and data.price > 0:
            return int(position_value / data.price)

        return 0

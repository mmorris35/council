"""
Ray Dalio Agent - All-Weather Portfolio.

File Name      : dalio.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL

Strategy:
- Risk parity across asset classes
- Balance for all economic environments
- Study macro cycles
- Rebalance to maintain target weights
"""
from datetime import datetime
from typing import List, Dict, Optional

from .base import BaseAgent, TradeRecommendation
from src.db import Portfolio
from src.db.models import AgentType, TransactionType
from src.utils import get_logger

logger = get_logger(__name__)

ALL_WEATHER_ALLOCATION = {
    "VTI": 0.30,    # 30% US Stocks
    "TLT": 0.40,    # 40% Long-term Treasury
    "IEI": 0.15,    # 15% Intermediate Treasury
    "GLD": 0.075,   # 7.5% Gold
    "DBC": 0.075,   # 7.5% Commodities
}


class DalioAgent(BaseAgent):
    """
    Ray Dalio's All-Weather portfolio philosophy.

    "He who lives by the crystal ball will eat shattered glass."

    Strategy:
    - Risk parity: balance risk, not dollars
    - Prepare for all economic environments
    - Growth rising/falling x Inflation rising/falling
    - Rebalance when drift exceeds threshold
    """

    agent_type = AgentType.DALIO
    agent_name = "Ray Dalio"
    description = "All-weather risk parity - prepared for any environment"

    REBALANCE_THRESHOLD = 0.05  # 5% drift triggers rebalance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_allocation = ALL_WEATHER_ALLOCATION

    def analyze_market(self) -> str:
        """Analyze macro environment."""
        today = datetime.now()

        environment = self._assess_environment()

        analysis = (
            f"Date: {today.date().isoformat()}\n"
            f"Philosophy: Balance risk across economic environments.\n\n"
            f"All-Weather Target Allocation:\n"
        )

        for symbol, weight in self.target_allocation.items():
            analysis += f"  - {symbol}: {weight*100:.1f}%\n"

        analysis += (
            f"\nEnvironment Assessment: {environment}\n\n"
            f"Quadrant Analysis:\n"
            f"  - Growth Rising + Inflation Rising: Commodities, TIPS\n"
            f"  - Growth Rising + Inflation Falling: Stocks\n"
            f"  - Growth Falling + Inflation Rising: Gold\n"
            f"  - Growth Falling + Inflation Falling: Bonds\n\n"
            f"Wisdom: 'Diversifying well is the most important thing you need to do "
            f"in order to invest well.'"
        )

        return analysis

    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """Generate rebalancing recommendations."""
        recommendations = []

        current_allocation = self._calculate_current_allocation(portfolio)

        total_value = portfolio.total_value

        for symbol, target_weight in self.target_allocation.items():
            current_weight = current_allocation.get(symbol, 0)
            drift = abs(current_weight - target_weight)

            if drift > self.REBALANCE_THRESHOLD:
                data = self.data.get_fundamentals(symbol)
                if not data:
                    continue

                target_value = total_value * target_weight
                current_value = total_value * current_weight

                if current_weight < target_weight:
                    value_to_buy = target_value - current_value
                    shares = int(value_to_buy / data.price)
                    if shares > 0 and value_to_buy <= portfolio.cash:
                        recommendations.append(TradeRecommendation(
                            action=TransactionType.BUY,
                            symbol=symbol,
                            shares=shares,
                            reasoning=f"Rebalance: {current_weight*100:.1f}% -> {target_weight*100:.1f}%",
                            confidence=0.85,
                        ))
                else:
                    value_to_sell = current_value - target_value
                    shares = int(value_to_sell / data.price)
                    position = next(
                        (p for p in portfolio.positions if p.symbol == symbol), None
                    )
                    if shares > 0 and position and position.shares >= shares:
                        recommendations.append(TradeRecommendation(
                            action=TransactionType.SELL,
                            symbol=symbol,
                            shares=shares,
                            reasoning=f"Rebalance: {current_weight*100:.1f}% -> {target_weight*100:.1f}%",
                            confidence=0.85,
                        ))

        if portfolio.cash > portfolio.total_value * 0.10:
            recommendations.extend(self._deploy_cash(portfolio))

        return recommendations

    def _calculate_current_allocation(
        self,
        portfolio: Portfolio
    ) -> Dict[str, float]:
        """Calculate current allocation percentages."""
        total = portfolio.total_value
        if total <= 0:
            return {}

        allocation = {}
        for position in portfolio.positions:
            allocation[position.symbol] = position.market_value / total

        return allocation

    def _deploy_cash(self, portfolio: Portfolio) -> List[TradeRecommendation]:
        """Deploy excess cash according to target allocation."""
        recommendations = []

        deployable = portfolio.cash * 0.9

        for symbol, weight in self.target_allocation.items():
            data = self.data.get_fundamentals(symbol)
            if not data:
                continue

            allocation_amount = deployable * weight
            shares = int(allocation_amount / data.price)

            if shares > 0:
                recommendations.append(TradeRecommendation(
                    action=TransactionType.BUY,
                    symbol=symbol,
                    shares=shares,
                    reasoning=f"Initial allocation: {weight*100:.1f}% of portfolio",
                    confidence=0.9,
                ))

        return recommendations

    def _assess_environment(self) -> str:
        """Assess current macro environment."""
        return "Balanced - maintaining all-weather allocation"

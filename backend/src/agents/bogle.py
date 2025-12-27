"""
John Bogle Agent - Passive Index Investing.

File Name      : bogle.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL

Strategy:
- Buy total market index (VTI) and bonds (BND)
- Minimal trading, rebalance annually
- Age-based allocation: (100 - age)% stocks
"""
from datetime import datetime, date
from typing import List

from .base import BaseAgent, TradeRecommendation
from src.db import Portfolio
from src.db.models import AgentType, TransactionType
from src.utils import get_logger

logger = get_logger(__name__)

# ETF symbols for passive investing
VTI = "VTI"  # Vanguard Total Stock Market
BND = "BND"  # Vanguard Total Bond Market


class BogleAgent(BaseAgent):
    """
    John Bogle's passive index investing philosophy.

    "Don't look for the needle in the haystack. Just buy the haystack."

    Strategy:
    - Buy and hold low-cost index funds
    - Maintain target allocation based on age
    - Rebalance only when significantly off target
    - Minimize trading and costs
    """

    agent_type = AgentType.BOGLE
    agent_name = "John Bogle"
    description = "Passive index investing - buy the haystack, keep costs low"

    def __init__(self, target_stock_pct: float = 0.70, **kwargs):
        """
        Initialize Bogle agent.

        Args:
            target_stock_pct: Target percentage in stocks (default 70%)
        """
        super().__init__(**kwargs)
        self.target_stock_pct = target_stock_pct
        self.rebalance_threshold = 0.05  # 5% deviation triggers rebalance

    def analyze_market(self) -> str:
        """
        Bogle doesn't analyze markets - time in market beats timing the market.
        """
        today = date.today()
        is_first_of_month = today.day <= 5

        analysis = (
            f"Date: {today.isoformat()}\n"
            f"Philosophy: Time in the market beats timing the market.\n"
            f"Action: {'Monthly investment day - deploying new capital' if is_first_of_month else 'Stay the course'}\n"
            f"Target Allocation: {self.target_stock_pct*100:.0f}% stocks / "
            f"{(1-self.target_stock_pct)*100:.0f}% bonds\n"
            f"Wisdom: 'The stock market is a giant distraction to the business of investing.'"
        )

        return analysis

    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """
        Generate recommendations - mostly do nothing, occasionally rebalance.
        """
        recommendations = []
        today = date.today()

        vti_position = next(
            (p for p in portfolio.positions if p.symbol == VTI), None
        )
        bnd_position = next(
            (p for p in portfolio.positions if p.symbol == BND), None
        )

        vti_value = vti_position.market_value if vti_position else 0
        bnd_value = bnd_position.market_value if bnd_position else 0
        total_invested = vti_value + bnd_value

        if portfolio.cash > 1000 and today.day <= 5:
            recommendations.extend(
                self._allocate_cash(portfolio.cash)
            )

        if total_invested > 0:
            current_stock_pct = vti_value / total_invested
            deviation = abs(current_stock_pct - self.target_stock_pct)

            if deviation > self.rebalance_threshold:
                recommendations.extend(
                    self._rebalance(portfolio, current_stock_pct)
                )

        return recommendations

    def _allocate_cash(self, cash: float) -> List[TradeRecommendation]:
        """Allocate new cash according to target allocation."""
        recommendations = []

        stock_allocation = cash * self.target_stock_pct
        bond_allocation = cash * (1 - self.target_stock_pct)

        vti_data = self.data.get_fundamentals(VTI)
        bnd_data = self.data.get_fundamentals(BND)

        if vti_data and vti_data.price > 0:
            vti_shares = int(stock_allocation / vti_data.price)
            if vti_shares > 0:
                recommendations.append(TradeRecommendation(
                    action=TransactionType.BUY,
                    symbol=VTI,
                    shares=vti_shares,
                    reasoning="Monthly allocation to total market index",
                    confidence=0.95,
                ))

        if bnd_data and bnd_data.price > 0:
            bnd_shares = int(bond_allocation / bnd_data.price)
            if bnd_shares > 0:
                recommendations.append(TradeRecommendation(
                    action=TransactionType.BUY,
                    symbol=BND,
                    shares=bnd_shares,
                    reasoning="Monthly allocation to total bond index",
                    confidence=0.95,
                ))

        return recommendations

    def _rebalance(
        self,
        portfolio: Portfolio,
        current_stock_pct: float
    ) -> List[TradeRecommendation]:
        """Rebalance portfolio to target allocation."""
        recommendations = []

        vti_position = next(
            (p for p in portfolio.positions if p.symbol == VTI), None
        )
        bnd_position = next(
            (p for p in portfolio.positions if p.symbol == BND), None
        )

        total_value = portfolio.total_value
        target_stock_value = total_value * self.target_stock_pct
        current_stock_value = vti_position.market_value if vti_position else 0

        vti_data = self.data.get_fundamentals(VTI)
        bnd_data = self.data.get_fundamentals(BND)

        if current_stock_pct > self.target_stock_pct:
            excess = current_stock_value - target_stock_value
            if vti_data and vti_data.price > 0:
                shares_to_sell = int(excess / vti_data.price)
                if shares_to_sell > 0:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.SELL,
                        symbol=VTI,
                        shares=shares_to_sell,
                        reasoning=f"Annual rebalance - stocks over target ({current_stock_pct*100:.1f}% vs {self.target_stock_pct*100:.1f}%)",
                        confidence=0.85,
                    ))
        else:
            deficit = target_stock_value - current_stock_value
            if vti_data and vti_data.price > 0 and portfolio.cash >= deficit:
                shares_to_buy = int(deficit / vti_data.price)
                if shares_to_buy > 0:
                    recommendations.append(TradeRecommendation(
                        action=TransactionType.BUY,
                        symbol=VTI,
                        shares=shares_to_buy,
                        reasoning=f"Annual rebalance - stocks under target ({current_stock_pct*100:.1f}% vs {self.target_stock_pct*100:.1f}%)",
                        confidence=0.85,
                    ))

        return recommendations

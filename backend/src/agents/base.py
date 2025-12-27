"""
Base agent class for all investor agents.

File Name      : base.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from src.db import DynamoDBClient, Portfolio, Position, Transaction, AgentRun
from src.db.models import AgentType, TransactionType
from src.data import YFinanceClient
from src.utils import get_logger, settings

logger = get_logger(__name__)


class TradeRecommendation:
    """A recommended trade from an agent."""

    def __init__(
        self,
        action: TransactionType,
        symbol: str,
        shares: float,
        reasoning: str,
        confidence: float = 0.5,
    ):
        self.action = action
        self.symbol = symbol
        self.shares = shares
        self.reasoning = reasoning
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "symbol": self.symbol,
            "shares": self.shares,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all investor agents.

    Each agent implements its own investment philosophy and decision-making logic.
    """

    agent_type: AgentType
    agent_name: str
    description: str

    def __init__(
        self,
        db_client: Optional[DynamoDBClient] = None,
        data_client: Optional[YFinanceClient] = None,
    ):
        self.db = db_client or DynamoDBClient()
        self.data = data_client or YFinanceClient()
        self.logger = get_logger(f"agent.{self.agent_type.value}")

    @abstractmethod
    def analyze_market(self) -> str:
        """
        Analyze current market conditions.

        Returns:
            Analysis text summarizing market conditions
        """
        pass

    @abstractmethod
    def generate_recommendations(
        self,
        portfolio: Portfolio,
    ) -> List[TradeRecommendation]:
        """
        Generate trade recommendations based on current portfolio and market.

        Args:
            portfolio: Current portfolio state

        Returns:
            List of trade recommendations
        """
        pass

    def run(self, user_id: str) -> AgentRun:
        """
        Execute a full agent run: analyze, recommend, execute.

        Args:
            user_id: User whose portfolio to manage

        Returns:
            AgentRun record of what happened
        """
        start_time = datetime.utcnow()
        self.logger.info(f"Starting {self.agent_name} run for user {user_id}")

        portfolio = self.db.get_portfolio(user_id, self.agent_type)
        if not portfolio:
            portfolio = self._initialize_portfolio(user_id)

        self._update_portfolio_prices(portfolio)
        value_before = portfolio.total_value

        analysis = self.analyze_market()
        self.logger.info(f"Analysis complete: {analysis[:100]}...")

        recommendations = self.generate_recommendations(portfolio)
        self.logger.info(f"Generated {len(recommendations)} recommendations")

        executed_trades = []
        for rec in recommendations:
            if rec.confidence >= 0.7:
                txn = self._execute_trade(portfolio, rec)
                if txn:
                    executed_trades.append(txn.transaction_id)

        self._update_portfolio_prices(portfolio)
        value_after = portfolio.total_value

        self.db.save_portfolio(portfolio)

        duration = (datetime.utcnow() - start_time).total_seconds()

        run = AgentRun(
            run_id=str(uuid.uuid4()),
            agent_type=self.agent_type,
            run_date=start_time,
            analysis=analysis,
            recommendations=[r.to_dict() for r in recommendations],
            executed_trades=executed_trades,
            portfolio_value_before=value_before,
            portfolio_value_after=value_after,
            duration_seconds=duration,
        )

        self.db.save_agent_run(run)
        self.logger.info(f"Run complete. Value: ${value_before:,.2f} -> ${value_after:,.2f}")

        return run

    def _initialize_portfolio(self, user_id: str) -> Portfolio:
        """Create a new portfolio with starting cash."""
        portfolio = Portfolio(
            portfolio_id=str(uuid.uuid4()),
            user_id=user_id,
            agent_type=self.agent_type,
            cash=settings.starting_portfolio_value,
            positions=[],
        )
        self.db.save_portfolio(portfolio)
        self.logger.info(f"Initialized new portfolio with ${settings.starting_portfolio_value:,.2f}")
        return portfolio

    def _update_portfolio_prices(self, portfolio: Portfolio) -> None:
        """Update current prices for all positions."""
        for position in portfolio.positions:
            data = self.data.get_fundamentals(position.symbol)
            if data:
                position.current_price = data.price

    def _execute_trade(
        self,
        portfolio: Portfolio,
        recommendation: TradeRecommendation,
    ) -> Optional[Transaction]:
        """
        Execute a trade recommendation.

        Args:
            portfolio: Portfolio to modify
            recommendation: Trade to execute

        Returns:
            Transaction record or None if failed
        """
        data = self.data.get_fundamentals(recommendation.symbol)
        if not data:
            self.logger.warning(f"Could not get price for {recommendation.symbol}")
            return None

        price = data.price
        total_cost = price * recommendation.shares

        if recommendation.action == TransactionType.BUY:
            if total_cost > portfolio.cash:
                affordable_shares = int(portfolio.cash / price)
                if affordable_shares <= 0:
                    self.logger.warning(f"Insufficient cash to buy {recommendation.symbol}")
                    return None
                recommendation.shares = affordable_shares
                total_cost = price * affordable_shares

            portfolio.cash -= total_cost

            existing = next(
                (p for p in portfolio.positions if p.symbol == recommendation.symbol),
                None
            )
            if existing:
                total_shares = existing.shares + recommendation.shares
                total_invested = (existing.shares * existing.avg_cost) + total_cost
                existing.avg_cost = total_invested / total_shares
                existing.shares = total_shares
                existing.current_price = price
            else:
                portfolio.positions.append(Position(
                    symbol=recommendation.symbol,
                    shares=recommendation.shares,
                    avg_cost=price,
                    current_price=price,
                ))

        elif recommendation.action == TransactionType.SELL:
            existing = next(
                (p for p in portfolio.positions if p.symbol == recommendation.symbol),
                None
            )
            if not existing:
                self.logger.warning(f"No position in {recommendation.symbol} to sell")
                return None

            shares_to_sell = min(recommendation.shares, existing.shares)
            proceeds = shares_to_sell * price
            portfolio.cash += proceeds

            existing.shares -= shares_to_sell
            if existing.shares <= 0:
                portfolio.positions = [
                    p for p in portfolio.positions if p.symbol != recommendation.symbol
                ]

        portfolio.updated_at = datetime.utcnow()

        txn = Transaction(
            transaction_id=str(uuid.uuid4()),
            portfolio_id=portfolio.portfolio_id,
            user_id=portfolio.user_id,
            agent_type=self.agent_type,
            transaction_type=recommendation.action,
            symbol=recommendation.symbol,
            shares=recommendation.shares,
            price=price,
            reasoning=recommendation.reasoning,
        )

        self.db.save_transaction(txn)
        self.logger.info(
            f"Executed {recommendation.action.value} {recommendation.shares} "
            f"{recommendation.symbol} @ ${price:.2f}"
        )

        return txn

    def get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of the portfolio state."""
        portfolio = self.db.get_portfolio(user_id, self.agent_type)
        if not portfolio:
            return {"error": "No portfolio found"}

        self._update_portfolio_prices(portfolio)

        return {
            "agent": self.agent_name,
            "total_value": portfolio.total_value,
            "cash": portfolio.cash,
            "positions": [
                {
                    "symbol": p.symbol,
                    "shares": p.shares,
                    "avg_cost": p.avg_cost,
                    "current_price": p.current_price,
                    "market_value": p.market_value,
                    "gain_loss": p.gain_loss,
                    "gain_loss_pct": p.gain_loss_pct,
                }
                for p in portfolio.positions
            ],
            "num_positions": len(portfolio.positions),
        }

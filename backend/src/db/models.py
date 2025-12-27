"""
Database models for Council.

File Name      : models.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    """Agent type enumeration."""
    BUFFETT = "buffett"
    GRAHAM = "graham"
    LYNCH = "lynch"
    DALIO = "dalio"
    BOGLE = "bogle"
    WOOD = "wood"


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"


class User(BaseModel):
    """User model."""
    user_id: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    email_alerts_enabled: bool = True

    def to_dynamo(self) -> Dict[str, Any]:
        return {
            "pk": f"USER#{self.user_id}",
            "sk": "PROFILE",
            "user_id": self.user_id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "email_alerts_enabled": self.email_alerts_enabled,
            "gsi1pk": f"EMAIL#{self.email}",
            "gsi1sk": "USER",
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "User":
        return cls(
            user_id=item["user_id"],
            email=item["email"],
            created_at=datetime.fromisoformat(item["created_at"]),
            email_alerts_enabled=item.get("email_alerts_enabled", True),
        )


class Position(BaseModel):
    """Single position in a portfolio."""
    symbol: str
    shares: float
    avg_cost: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def gain_loss(self) -> float:
        return (self.current_price - self.avg_cost) * self.shares

    @property
    def gain_loss_pct(self) -> float:
        if self.avg_cost == 0:
            return 0.0
        return (self.current_price - self.avg_cost) / self.avg_cost


class Portfolio(BaseModel):
    """Portfolio model."""
    portfolio_id: str
    user_id: str
    agent_type: AgentType
    cash: float
    positions: List[Position] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total_value(self) -> float:
        positions_value = sum(p.market_value for p in self.positions)
        return self.cash + positions_value

    def to_dynamo(self) -> Dict[str, Any]:
        positions_data = [
            {
                "symbol": p.symbol,
                "shares": str(p.shares),
                "avg_cost": str(p.avg_cost),
                "current_price": str(p.current_price),
            }
            for p in self.positions
        ]
        return {
            "pk": f"USER#{self.user_id}",
            "sk": f"PORTFOLIO#{self.agent_type.value}",
            "portfolio_id": self.portfolio_id,
            "user_id": self.user_id,
            "agent_type": self.agent_type.value,
            "cash": str(self.cash),
            "positions": positions_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "gsi1pk": f"AGENT#{self.agent_type.value}",
            "gsi1sk": f"USER#{self.user_id}",
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "Portfolio":
        positions = [
            Position(
                symbol=p["symbol"],
                shares=float(p["shares"]),
                avg_cost=float(p["avg_cost"]),
                current_price=float(p["current_price"]),
            )
            for p in item.get("positions", [])
        ]
        return cls(
            portfolio_id=item["portfolio_id"],
            user_id=item["user_id"],
            agent_type=AgentType(item["agent_type"]),
            cash=float(item["cash"]),
            positions=positions,
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
        )


class Transaction(BaseModel):
    """Transaction model."""
    transaction_id: str
    portfolio_id: str
    user_id: str
    agent_type: AgentType
    transaction_type: TransactionType
    symbol: str
    shares: float
    price: float
    reasoning: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total_value(self) -> float:
        return self.shares * self.price

    def to_dynamo(self) -> Dict[str, Any]:
        return {
            "pk": f"USER#{self.user_id}",
            "sk": f"TXN#{self.created_at.isoformat()}#{self.transaction_id}",
            "transaction_id": self.transaction_id,
            "portfolio_id": self.portfolio_id,
            "user_id": self.user_id,
            "agent_type": self.agent_type.value,
            "transaction_type": self.transaction_type.value,
            "symbol": self.symbol,
            "shares": str(self.shares),
            "price": str(self.price),
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat(),
            "gsi1pk": f"AGENT#{self.agent_type.value}",
            "gsi1sk": f"TXN#{self.created_at.isoformat()}",
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "Transaction":
        return cls(
            transaction_id=item["transaction_id"],
            portfolio_id=item["portfolio_id"],
            user_id=item["user_id"],
            agent_type=AgentType(item["agent_type"]),
            transaction_type=TransactionType(item["transaction_type"]),
            symbol=item["symbol"],
            shares=float(item["shares"]),
            price=float(item["price"]),
            reasoning=item.get("reasoning", ""),
            created_at=datetime.fromisoformat(item["created_at"]),
        )


class AgentRun(BaseModel):
    """Record of an agent's daily run."""
    run_id: str
    agent_type: AgentType
    run_date: datetime
    analysis: str
    recommendations: List[Dict[str, Any]] = []
    executed_trades: List[str] = []  # Transaction IDs
    portfolio_value_before: float
    portfolio_value_after: float
    duration_seconds: float

    def to_dynamo(self) -> Dict[str, Any]:
        return {
            "pk": f"AGENT#{self.agent_type.value}",
            "sk": f"RUN#{self.run_date.date().isoformat()}",
            "run_id": self.run_id,
            "agent_type": self.agent_type.value,
            "run_date": self.run_date.isoformat(),
            "analysis": self.analysis,
            "recommendations": self.recommendations,
            "executed_trades": self.executed_trades,
            "portfolio_value_before": str(self.portfolio_value_before),
            "portfolio_value_after": str(self.portfolio_value_after),
            "duration_seconds": str(self.duration_seconds),
            "gsi1pk": f"DATE#{self.run_date.date().isoformat()}",
            "gsi1sk": f"AGENT#{self.agent_type.value}",
        }

    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "AgentRun":
        return cls(
            run_id=item["run_id"],
            agent_type=AgentType(item["agent_type"]),
            run_date=datetime.fromisoformat(item["run_date"]),
            analysis=item["analysis"],
            recommendations=item.get("recommendations", []),
            executed_trades=item.get("executed_trades", []),
            portfolio_value_before=float(item["portfolio_value_before"]),
            portfolio_value_after=float(item["portfolio_value_after"]),
            duration_seconds=float(item["duration_seconds"]),
        )

"""
DynamoDB access layer for Council.

File Name      : dynamo.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, boto3
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Optional, List, Dict, Any
from src.utils import get_logger, settings
from .models import User, Portfolio, Transaction, AgentRun, AgentType

logger = get_logger(__name__)


class DynamoDBClient:
    """DynamoDB access client."""

    def __init__(self, table_name: Optional[str] = None):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.table_name = table_name or f"{settings.dynamodb_table_prefix}-main"
        self.table = self.dynamodb.Table(self.table_name)

    # User operations
    def create_user(self, user: User) -> bool:
        """Create a new user."""
        try:
            self.table.put_item(
                Item=user.to_dynamo(),
                ConditionExpression="attribute_not_exists(pk)"
            )
            logger.info(f"Created user {user.user_id}")
            return True
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            logger.warning(f"User {user.user_id} already exists")
            return False
        except Exception as exc:
            logger.error(f"Error creating user: {exc}")
            return False

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        try:
            response = self.table.get_item(
                Key={"pk": f"USER#{user_id}", "sk": "PROFILE"}
            )
            item = response.get("Item")
            return User.from_dynamo(item) if item else None
        except Exception as exc:
            logger.error(f"Error getting user {user_id}: {exc}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email using GSI."""
        try:
            response = self.table.query(
                IndexName="gsi1",
                KeyConditionExpression=Key("gsi1pk").eq(f"EMAIL#{email}") & Key("gsi1sk").eq("USER")
            )
            items = response.get("Items", [])
            return User.from_dynamo(items[0]) if items else None
        except Exception as exc:
            logger.error(f"Error getting user by email {email}: {exc}")
            return None

    # Portfolio operations
    def save_portfolio(self, portfolio: Portfolio) -> bool:
        """Save or update a portfolio."""
        try:
            self.table.put_item(Item=portfolio.to_dynamo())
            logger.info(f"Saved portfolio {portfolio.portfolio_id} for {portfolio.agent_type.value}")
            return True
        except Exception as exc:
            logger.error(f"Error saving portfolio: {exc}")
            return False

    def get_portfolio(self, user_id: str, agent_type: AgentType) -> Optional[Portfolio]:
        """Get a user's portfolio for a specific agent."""
        try:
            response = self.table.get_item(
                Key={"pk": f"USER#{user_id}", "sk": f"PORTFOLIO#{agent_type.value}"}
            )
            item = response.get("Item")
            return Portfolio.from_dynamo(item) if item else None
        except Exception as exc:
            logger.error(f"Error getting portfolio: {exc}")
            return None

    def get_user_portfolios(self, user_id: str) -> List[Portfolio]:
        """Get all portfolios for a user."""
        try:
            response = self.table.query(
                KeyConditionExpression=Key("pk").eq(f"USER#{user_id}") & Key("sk").begins_with("PORTFOLIO#")
            )
            return [Portfolio.from_dynamo(item) for item in response.get("Items", [])]
        except Exception as exc:
            logger.error(f"Error getting user portfolios: {exc}")
            return []

    # Transaction operations
    def save_transaction(self, transaction: Transaction) -> bool:
        """Save a transaction."""
        try:
            self.table.put_item(Item=transaction.to_dynamo())
            logger.info(f"Saved transaction {transaction.transaction_id}")
            return True
        except Exception as exc:
            logger.error(f"Error saving transaction: {exc}")
            return False

    def get_user_transactions(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Transaction]:
        """Get recent transactions for a user."""
        try:
            response = self.table.query(
                KeyConditionExpression=Key("pk").eq(f"USER#{user_id}") & Key("sk").begins_with("TXN#"),
                ScanIndexForward=False,  # Newest first
                Limit=limit
            )
            return [Transaction.from_dynamo(item) for item in response.get("Items", [])]
        except Exception as exc:
            logger.error(f"Error getting transactions: {exc}")
            return []

    # Agent run operations
    def save_agent_run(self, run: AgentRun) -> bool:
        """Save an agent run record."""
        try:
            self.table.put_item(Item=run.to_dynamo())
            logger.info(f"Saved agent run {run.run_id}")
            return True
        except Exception as exc:
            logger.error(f"Error saving agent run: {exc}")
            return False

    def get_agent_runs(
        self,
        agent_type: AgentType,
        limit: int = 30
    ) -> List[AgentRun]:
        """Get recent runs for an agent."""
        try:
            response = self.table.query(
                KeyConditionExpression=Key("pk").eq(f"AGENT#{agent_type.value}") & Key("sk").begins_with("RUN#"),
                ScanIndexForward=False,
                Limit=limit
            )
            return [AgentRun.from_dynamo(item) for item in response.get("Items", [])]
        except Exception as exc:
            logger.error(f"Error getting agent runs: {exc}")
            return []

    def get_latest_agent_run(self, agent_type: AgentType) -> Optional[AgentRun]:
        """Get the most recent run for an agent."""
        runs = self.get_agent_runs(agent_type, limit=1)
        return runs[0] if runs else None

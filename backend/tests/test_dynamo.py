"""
Tests for DynamoDB client.

File Name      : test_dynamo.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest, moto
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import boto3
from moto import mock_aws
from datetime import datetime
from src.db import DynamoDBClient, User, Portfolio, Position, Transaction, AgentRun
from src.db.models import AgentType, TransactionType


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="council-test-main",
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "gsi1pk", "AttributeType": "S"},
                {"AttributeName": "gsi1sk", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsi1",
                    "KeySchema": [
                        {"AttributeName": "gsi1pk", "KeyType": "HASH"},
                        {"AttributeName": "gsi1sk", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield table


@pytest.fixture
def client(dynamodb_table):
    """Create a DynamoDB client with mock table."""
    with mock_aws():
        return DynamoDBClient(table_name="council-test-main")


class TestDynamoDBClient:
    """Tests for DynamoDBClient."""

    def test_create_and_get_user(self, client):
        """Test user creation and retrieval."""
        user = User(user_id="user123", email="test@example.com")

        assert client.create_user(user) is True

        retrieved = client.get_user("user123")
        assert retrieved is not None
        assert retrieved.email == "test@example.com"

    def test_get_user_by_email(self, client):
        """Test user lookup by email."""
        user = User(user_id="user456", email="lookup@example.com")
        client.create_user(user)

        retrieved = client.get_user_by_email("lookup@example.com")
        assert retrieved is not None
        assert retrieved.user_id == "user456"

    def test_save_and_get_portfolio(self, client):
        """Test portfolio operations."""
        portfolio = Portfolio(
            portfolio_id="port123",
            user_id="user123",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[
                Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
            ],
        )

        assert client.save_portfolio(portfolio) is True

        retrieved = client.get_portfolio("user123", AgentType.BUFFETT)
        assert retrieved is not None
        assert retrieved.cash == 100000.0
        assert len(retrieved.positions) == 1

    def test_save_and_get_transactions(self, client):
        """Test transaction operations."""
        txn = Transaction(
            transaction_id="txn123",
            portfolio_id="port123",
            user_id="user123",
            agent_type=AgentType.BUFFETT,
            transaction_type=TransactionType.BUY,
            symbol="AAPL",
            shares=100,
            price=150.0,
            reasoning="Strong moat",
        )

        assert client.save_transaction(txn) is True

        transactions = client.get_user_transactions("user123")
        assert len(transactions) == 1
        assert transactions[0].symbol == "AAPL"

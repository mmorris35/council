# Development Plan: Council

## Overview

| Field | Value |
|-------|-------|
| **Project** | Council |
| **Start Date** | 2024-12-27 |
| **Target Completion** | 2024-01-03 |
| **Methodology** | Haiku-executable subtasks |

## Architecture

```
council/
├── backend/
│   ├── src/
│   │   ├── agents/           # 6 investor agent implementations
│   │   │   ├── base.py
│   │   │   ├── buffett.py
│   │   │   ├── graham.py
│   │   │   ├── lynch.py
│   │   │   ├── dalio.py
│   │   │   ├── bogle.py
│   │   │   └── wood.py
│   │   ├── data/             # Market data fetchers
│   │   │   ├── yfinance_client.py
│   │   │   ├── sec_edgar.py
│   │   │   ├── ark_holdings.py
│   │   │   └── fred_client.py
│   │   ├── portfolio/        # Paper trading
│   │   │   ├── manager.py
│   │   │   └── models.py
│   │   ├── alerts/           # Email notifications
│   │   │   └── ses_client.py
│   │   ├── api/              # Lambda handlers
│   │   │   ├── agents.py
│   │   │   ├── portfolios.py
│   │   │   ├── auth.py
│   │   │   └── dashboard.py
│   │   ├── db/               # DynamoDB access
│   │   │   └── dynamo.py
│   │   ├── scheduler/        # Scheduled job handlers
│   │   │   └── daily_run.py
│   │   └── utils/
│   │       ├── logging_config.py
│   │       └── config.py
│   ├── tests/
│   ├── template.yaml         # AWS SAM template
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   ├── package.json
│   └── index.html
└── docs/
```

---

## Phase 0: Project Setup

### Task 0.1: Initialize Project Structure

**Subtask 0.1.1: Create Backend Scaffolding (Single Session)**

**Prerequisites**:
- None (first task)

**Deliverables**:
- [ ] `backend/` directory structure created
- [ ] `backend/requirements.txt` with all dependencies
- [ ] `backend/src/utils/logging_config.py` centralized logging
- [ ] `backend/src/utils/config.py` environment configuration
- [ ] Virtual environment created and activated
- [ ] Basic pytest setup

**Technology Decisions**:
- Python 3.11 for Lambda compatibility
- boto3 for AWS services
- yfinance for market data
- pydantic for data validation

**Files to Create**:
- `backend/requirements.txt`
- `backend/src/__init__.py`
- `backend/src/utils/__init__.py`
- `backend/src/utils/logging_config.py`
- `backend/src/utils/config.py`
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`

**Complete Code**:

Create `backend/requirements.txt`:
```
boto3>=1.34.0
yfinance>=0.2.36
pandas>=2.1.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
requests>=2.31.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
moto>=4.2.0
python-dateutil>=2.8.0
```

Create `backend/src/__init__.py`:
```python
"""Council - Legendary Investor AI Agents."""
```

Create `backend/src/utils/__init__.py`:
```python
"""Utility modules for Council."""
from .logging_config import get_logger
from .config import settings

__all__ = ["get_logger", "settings"]
```

Create `backend/src/utils/logging_config.py`:
```python
"""
Centralized logging configuration for Council.

File Name      : logging_config.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional logging level override
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    if level is not None:
        logger.setLevel(level)
    elif logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
    
    return logger
```

Create `backend/src/utils/config.py`:
```python
"""
Environment configuration for Council.

File Name      : config.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    dynamodb_table_prefix: str = Field(default="council", alias="DYNAMODB_TABLE_PREFIX")
    ses_sender_email: str = Field(default="", alias="SES_SENDER_EMAIL")
    
    # API Keys (optional for free tier sources)
    alpha_vantage_key: Optional[str] = Field(default=None, alias="ALPHA_VANTAGE_KEY")
    fred_api_key: Optional[str] = Field(default=None, alias="FRED_API_KEY")
    
    # Application Settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Agent Configuration
    starting_portfolio_value: float = Field(default=100000.0)
    max_position_pct: float = Field(default=0.20)  # 20% max per position
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

Create `backend/tests/__init__.py`:
```python
"""Test suite for Council."""
```

Create `backend/tests/conftest.py`:
```python
"""
Pytest configuration and fixtures for Council tests.

File Name      : conftest.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_TABLE_PREFIX", "council-test")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("SES_SENDER_EMAIL", "test@example.com")


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "AAPL": {
            "price": 175.50,
            "pe_ratio": 28.5,
            "pb_ratio": 45.2,
            "market_cap": 2800000000000,
            "dividend_yield": 0.005,
            "current_ratio": 1.0,
            "debt_to_equity": 1.8,
        },
        "BRK-B": {
            "price": 365.00,
            "pe_ratio": 9.5,
            "pb_ratio": 1.4,
            "market_cap": 800000000000,
            "dividend_yield": 0.0,
            "current_ratio": 3.2,
            "debt_to_equity": 0.2,
        },
    }
```

**Verification**:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from src.utils import get_logger, settings; print(settings.environment)"
pytest --collect-only
```

**Success Criteria**:
- [ ] Virtual environment created
- [ ] All dependencies install without errors
- [ ] Config loads default values correctly
- [ ] Logger produces formatted output
- [ ] pytest discovers test directory

**Completion Notes**:
- **Implementation**: (to be filled)
- **Files Created**: (to be filled)
- **Tests**: (to be filled)
- **Build**: (to be filled)
- **Branch**: feature/0-1-project-setup

---

**Subtask 0.1.2: Create AWS SAM Template (Single Session)**

**Prerequisites**:
- [x] 0.1.1: Create Backend Scaffolding

**Deliverables**:
- [ ] `backend/template.yaml` AWS SAM infrastructure
- [ ] DynamoDB tables defined (users, portfolios, transactions, agent_runs)
- [ ] Lambda functions defined
- [ ] API Gateway endpoints defined
- [ ] EventBridge scheduled rules defined
- [ ] IAM roles with least privilege

**Technology Decisions**:
- AWS SAM for IaC (simpler than CDK for this scope)
- Single-table DynamoDB design with GSIs
- REST API Gateway (not HTTP API for more features)

**Files to Create**:
- `backend/template.yaml`
- `backend/samconfig.toml`

**Complete Code**:

Create `backend/template.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Council - Legendary Investor AI Agents

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: python3.11
    Environment:
      Variables:
        DYNAMODB_TABLE_PREFIX: !Ref TablePrefix
        SES_SENDER_EMAIL: !Ref SenderEmail
        ENVIRONMENT: !Ref Environment
        LOG_LEVEL: INFO

Parameters:
  TablePrefix:
    Type: String
    Default: council
  SenderEmail:
    Type: String
    Default: noreply@council.example.com
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - development
      - production

Resources:
  # DynamoDB Tables
  MainTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${TablePrefix}-main
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: gsi1pk
          AttributeType: S
        - AttributeName: gsi1sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: gsi1
          KeySchema:
            - AttributeName: gsi1pk
              KeyType: HASH
            - AttributeName: gsi1sk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # API Gateway
  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn

  # Cognito User Pool
  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub ${TablePrefix}-users
      AutoVerifiedAttributes:
        - email
      UsernameAttributes:
        - email
      Policies:
        PasswordPolicy:
          MinimumLength: 8
          RequireLowercase: true
          RequireNumbers: true
          RequireSymbols: false
          RequireUppercase: true

  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: !Sub ${TablePrefix}-web-client
      UserPoolId: !Ref UserPool
      GenerateSecret: false
      ExplicitAuthFlows:
        - ALLOW_USER_PASSWORD_AUTH
        - ALLOW_REFRESH_TOKEN_AUTH
        - ALLOW_USER_SRP_AUTH

  # Lambda Functions
  DashboardFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${TablePrefix}-dashboard
      CodeUri: src/
      Handler: api.dashboard.handler
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref MainTable
      Events:
        GetDashboard:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /dashboard
            Method: GET
        GetAgentDetail:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /agents/{agent_id}
            Method: GET

  PortfolioFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${TablePrefix}-portfolio
      CodeUri: src/
      Handler: api.portfolios.handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref MainTable
      Events:
        GetPortfolio:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /portfolios/{portfolio_id}
            Method: GET
        ListPortfolios:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /portfolios
            Method: GET

  AgentRunFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${TablePrefix}-agent-run
      CodeUri: src/
      Handler: scheduler.daily_run.handler
      Timeout: 300
      MemorySize: 512
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref MainTable
        - SESCrudPolicy:
            IdentityName: !Ref SenderEmail
      Events:
        DailySchedule:
          Type: Schedule
          Properties:
            Schedule: cron(0 14 ? * MON-FRI *)  # 2 PM UTC = 9 AM EST
            Description: Run all agents daily on market days

  AlertFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${TablePrefix}-alerts
      CodeUri: src/
      Handler: alerts.ses_client.handler
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref MainTable
        - SESCrudPolicy:
            IdentityName: !Ref SenderEmail

  AuthFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${TablePrefix}-auth
      CodeUri: src/
      Handler: api.auth.handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref MainTable
      Events:
        Register:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /auth/register
            Method: POST
            Auth:
              Authorizer: NONE
        Profile:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /auth/profile
            Method: GET

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Environment}
  UserPoolId:
    Description: Cognito User Pool ID
    Value: !Ref UserPool
  UserPoolClientId:
    Description: Cognito User Pool Client ID
    Value: !Ref UserPoolClient
  MainTableName:
    Description: DynamoDB Main Table Name
    Value: !Ref MainTable
```

Create `backend/samconfig.toml`:
```toml
version = 0.1

[default.deploy.parameters]
stack_name = "council"
resolve_s3 = true
s3_prefix = "council"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
parameter_overrides = "TablePrefix=council Environment=production"
```

**Verification**:
```bash
cd backend
sam validate
sam build --use-container
```

**Success Criteria**:
- [ ] SAM template validates without errors
- [ ] All resources defined correctly
- [ ] IAM policies follow least privilege
- [ ] EventBridge cron schedule is correct

**Completion Notes**:
- **Implementation**: (to be filled)
- **Files Created**: (to be filled)
- **Branch**: feature/0-1-project-setup

---

### Task 0.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/0-1-project-setup`
- [ ] Delete branch: `git branch -d feature/0-1-project-setup`

---

## Phase 1: Data Layer

### Task 1.1: Implement Data Fetchers

**Subtask 1.1.1: Yahoo Finance Client (Single Session)**

**Prerequisites**:
- [x] 0.1.2: Create AWS SAM Template

**Deliverables**:
- [ ] `backend/src/data/__init__.py` module init
- [ ] `backend/src/data/yfinance_client.py` stock data fetcher
- [ ] Support for price, fundamentals, historical data
- [ ] Error handling and retry logic
- [ ] Unit tests with mocked responses

**Technology Decisions**:
- yfinance library (unofficial Yahoo Finance API)
- Caching layer to reduce API calls
- Batch fetching for efficiency

**Files to Create**:
- `backend/src/data/__init__.py`
- `backend/src/data/yfinance_client.py`
- `backend/tests/test_yfinance_client.py`

**Complete Code**:

Create `backend/src/data/__init__.py`:
```python
"""Data fetching modules for Council."""
from .yfinance_client import YFinanceClient

__all__ = ["YFinanceClient"]
```

Create `backend/src/data/yfinance_client.py`:
```python
"""
Yahoo Finance data client for stock information.

File Name      : yfinance_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, yfinance
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from src.utils import get_logger

logger = get_logger(__name__)


class StockFundamentals(BaseModel):
    """Stock fundamental data model."""
    symbol: str
    price: float
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    return_on_equity: Optional[float] = None
    beta: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class YFinanceClient:
    """Client for fetching stock data from Yahoo Finance."""
    
    def __init__(self):
        self._cache: Dict[str, StockFundamentals] = {}
        self._cache_ttl = timedelta(minutes=15)
    
    def get_fundamentals(self, symbol: str, use_cache: bool = True) -> Optional[StockFundamentals]:
        """
        Fetch fundamental data for a stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            use_cache: Whether to use cached data if available
            
        Returns:
            StockFundamentals or None if fetch fails
        """
        cache_key = symbol.upper()
        
        if use_cache and cache_key in self._cache:
            cached = self._cache[cache_key]
            if datetime.utcnow() - cached.fetched_at < self._cache_ttl:
                logger.debug(f"Cache hit for {symbol}")
                return cached
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or "regularMarketPrice" not in info:
                logger.warning(f"No data found for {symbol}")
                return None
            
            fundamentals = StockFundamentals(
                symbol=cache_key,
                price=info.get("regularMarketPrice", info.get("currentPrice", 0)),
                pe_ratio=info.get("trailingPE"),
                pb_ratio=info.get("priceToBook"),
                ps_ratio=info.get("priceToSalesTrailing12Months"),
                peg_ratio=info.get("pegRatio"),
                market_cap=info.get("marketCap"),
                dividend_yield=info.get("dividendYield"),
                current_ratio=info.get("currentRatio"),
                debt_to_equity=info.get("debtToEquity"),
                revenue_growth=info.get("revenueGrowth"),
                earnings_growth=info.get("earningsGrowth"),
                profit_margin=info.get("profitMargins"),
                return_on_equity=info.get("returnOnEquity"),
                beta=info.get("beta"),
                fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=info.get("fiftyTwoWeekLow"),
                sector=info.get("sector"),
                industry=info.get("industry"),
            )
            
            self._cache[cache_key] = fundamentals
            logger.info(f"Fetched fundamentals for {symbol}: price=${fundamentals.price:.2f}")
            return fundamentals
            
        except Exception as exc:
            logger.error(f"Error fetching {symbol}: {exc}")
            return None
    
    def get_fundamentals_batch(self, symbols: List[str]) -> Dict[str, StockFundamentals]:
        """
        Fetch fundamentals for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            Dict mapping symbols to their fundamentals
        """
        results = {}
        for symbol in symbols:
            data = self.get_fundamentals(symbol)
            if data:
                results[symbol.upper()] = data
        return results
    
    def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data.
        
        Args:
            symbol: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
            
            if history.empty:
                logger.warning(f"No historical data for {symbol}")
                return None
            
            logger.info(f"Fetched {len(history)} rows of history for {symbol}")
            return history
            
        except Exception as exc:
            logger.error(f"Error fetching history for {symbol}: {exc}")
            return None
    
    def get_sp500_symbols(self) -> List[str]:
        """
        Get list of S&P 500 constituent symbols.
        
        Returns:
            List of ticker symbols
        """
        try:
            table = pd.read_html(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )[0]
            symbols = table["Symbol"].str.replace(".", "-", regex=False).tolist()
            logger.info(f"Fetched {len(symbols)} S&P 500 symbols")
            return symbols
        except Exception as exc:
            logger.error(f"Error fetching S&P 500 list: {exc}")
            return []
    
    def clear_cache(self):
        """Clear the fundamentals cache."""
        self._cache.clear()
        logger.info("Cache cleared")
```

Create `backend/tests/test_yfinance_client.py`:
```python
"""
Tests for Yahoo Finance client.

File Name      : test_yfinance_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import patch, MagicMock
from src.data.yfinance_client import YFinanceClient, StockFundamentals


class TestYFinanceClient:
    """Tests for YFinanceClient."""
    
    @pytest.fixture
    def client(self):
        """Create a fresh client for each test."""
        return YFinanceClient()
    
    @pytest.fixture
    def mock_ticker_info(self):
        """Mock ticker info response."""
        return {
            "regularMarketPrice": 175.50,
            "trailingPE": 28.5,
            "priceToBook": 45.2,
            "marketCap": 2800000000000,
            "dividendYield": 0.005,
            "currentRatio": 1.0,
            "debtToEquity": 180,
            "sector": "Technology",
            "industry": "Consumer Electronics",
        }
    
    def test_get_fundamentals_success(self, client, mock_ticker_info):
        """Test successful fundamentals fetch."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker
            
            result = client.get_fundamentals("AAPL")
            
            assert result is not None
            assert result.symbol == "AAPL"
            assert result.price == 175.50
            assert result.pe_ratio == 28.5
            assert result.sector == "Technology"
    
    def test_get_fundamentals_cache(self, client, mock_ticker_info):
        """Test that caching works."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker
            
            result1 = client.get_fundamentals("AAPL")
            result2 = client.get_fundamentals("AAPL")
            
            assert mock_ticker_class.call_count == 1
            assert result1.symbol == result2.symbol
    
    def test_get_fundamentals_no_data(self, client):
        """Test handling of missing data."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = {}
            mock_ticker_class.return_value = mock_ticker
            
            result = client.get_fundamentals("INVALID")
            
            assert result is None
    
    def test_get_fundamentals_batch(self, client, mock_ticker_info):
        """Test batch fetching."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker
            
            results = client.get_fundamentals_batch(["AAPL", "MSFT"])
            
            assert len(results) == 2
            assert "AAPL" in results
            assert "MSFT" in results
    
    def test_clear_cache(self, client, mock_ticker_info):
        """Test cache clearing."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.info = mock_ticker_info
            mock_ticker_class.return_value = mock_ticker
            
            client.get_fundamentals("AAPL")
            assert len(client._cache) == 1
            
            client.clear_cache()
            assert len(client._cache) == 0
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_yfinance_client.py -v
python -c "from src.data import YFinanceClient; c = YFinanceClient(); print(c.get_fundamentals('AAPL'))"
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Live fetch returns data for valid symbol
- [ ] Cache prevents duplicate API calls
- [ ] Error handling works for invalid symbols

**Completion Notes**:
- **Implementation**: (to be filled)
- **Files Created**: (to be filled)
- **Tests**: (to be filled)
- **Branch**: feature/1-1-data-fetchers

---

**Subtask 1.1.2: SEC EDGAR Client (Single Session)**

**Prerequisites**:
- [x] 1.1.1: Yahoo Finance Client

**Deliverables**:
- [ ] `backend/src/data/sec_edgar.py` 13F filing fetcher
- [ ] Parse holdings from XML filings
- [ ] Compare holdings between periods
- [ ] Unit tests

**Files to Create**:
- `backend/src/data/sec_edgar.py`
- `backend/tests/test_sec_edgar.py`

**Complete Code**:

Create `backend/src/data/sec_edgar.py`:
```python
"""
SEC EDGAR client for 13F filings.

File Name      : sec_edgar.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel
from src.utils import get_logger

logger = get_logger(__name__)

SEC_BASE_URL = "https://www.sec.gov"
SEC_HEADERS = {
    "User-Agent": "Council/1.0 (contact@example.com)",
    "Accept-Encoding": "gzip, deflate",
}

# Known CIK numbers for major investors
KNOWN_CIKS = {
    "berkshire": "0001067983",  # Berkshire Hathaway
    "bridgewater": "0001350694",  # Bridgewater Associates
}


class Holding(BaseModel):
    """Single holding from 13F filing."""
    name: str
    cusip: str
    value: float  # In thousands
    shares: int
    share_type: str  # SH (shares) or PRN (principal)


class Filing13F(BaseModel):
    """13F filing data."""
    cik: str
    company_name: str
    filing_date: datetime
    report_date: datetime
    holdings: List[Holding]
    total_value: float


class SECEdgarClient:
    """Client for fetching SEC EDGAR 13F filings."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(SEC_HEADERS)
    
    def get_latest_13f(self, cik: str) -> Optional[Filing13F]:
        """
        Fetch the latest 13F filing for a company.
        
        Args:
            cik: Central Index Key (company identifier)
            
        Returns:
            Filing13F or None if not found
        """
        cik_padded = cik.zfill(10)
        
        try:
            submissions_url = f"{SEC_BASE_URL}/cgi-bin/browse-edgar"
            params = {
                "action": "getcompany",
                "CIK": cik_padded,
                "type": "13F-HR",
                "dateb": "",
                "owner": "include",
                "count": "10",
                "output": "atom",
            }
            
            response = self.session.get(submissions_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            entries = root.findall("atom:entry", ns)
            if not entries:
                logger.warning(f"No 13F filings found for CIK {cik}")
                return None
            
            latest_entry = entries[0]
            filing_link = latest_entry.find("atom:link", ns).get("href")
            
            accession_number = filing_link.split("/")[-1].replace("-index.htm", "")
            
            return self._parse_13f_filing(cik_padded, accession_number)
            
        except Exception as exc:
            logger.error(f"Error fetching 13F for CIK {cik}: {exc}")
            return None
    
    def _parse_13f_filing(self, cik: str, accession_number: str) -> Optional[Filing13F]:
        """Parse a 13F filing from its accession number."""
        accession_formatted = accession_number.replace("-", "")
        
        info_table_url = (
            f"{SEC_BASE_URL}/Archives/edgar/data/{cik.lstrip('0')}/"
            f"{accession_formatted}/infotable.xml"
        )
        
        try:
            response = self.session.get(info_table_url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            ns = {
                "ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"
            }
            
            holdings = []
            for info in root.findall(".//ns:infoTable", ns):
                name_elem = info.find("ns:nameOfIssuer", ns)
                cusip_elem = info.find("ns:cusip", ns)
                value_elem = info.find("ns:value", ns)
                shares_elem = info.find(".//ns:sshPrnamt", ns)
                share_type_elem = info.find(".//ns:sshPrnamtType", ns)
                
                if all([name_elem, cusip_elem, value_elem, shares_elem]):
                    holdings.append(Holding(
                        name=name_elem.text or "",
                        cusip=cusip_elem.text or "",
                        value=float(value_elem.text or 0),
                        shares=int(shares_elem.text or 0),
                        share_type=share_type_elem.text if share_type_elem is not None else "SH",
                    ))
            
            total_value = sum(h.value for h in holdings)
            
            filing = Filing13F(
                cik=cik,
                company_name="",
                filing_date=datetime.utcnow(),
                report_date=datetime.utcnow(),
                holdings=holdings,
                total_value=total_value,
            )
            
            logger.info(f"Parsed 13F with {len(holdings)} holdings, total value ${total_value:,.0f}K")
            return filing
            
        except Exception as exc:
            logger.error(f"Error parsing 13F filing: {exc}")
            return None
    
    def get_berkshire_holdings(self) -> Optional[Filing13F]:
        """Convenience method to get Berkshire Hathaway holdings."""
        return self.get_latest_13f(KNOWN_CIKS["berkshire"])
    
    def compare_holdings(
        self,
        current: Filing13F,
        previous: Filing13F
    ) -> Dict[str, List[Holding]]:
        """
        Compare two filings to find changes.
        
        Returns:
            Dict with 'added', 'removed', 'increased', 'decreased' keys
        """
        current_cusips = {h.cusip: h for h in current.holdings}
        previous_cusips = {h.cusip: h for h in previous.holdings}
        
        added = [h for c, h in current_cusips.items() if c not in previous_cusips]
        removed = [h for c, h in previous_cusips.items() if c not in current_cusips]
        
        increased = []
        decreased = []
        
        for cusip, current_holding in current_cusips.items():
            if cusip in previous_cusips:
                prev_shares = previous_cusips[cusip].shares
                if current_holding.shares > prev_shares:
                    increased.append(current_holding)
                elif current_holding.shares < prev_shares:
                    decreased.append(current_holding)
        
        return {
            "added": added,
            "removed": removed,
            "increased": increased,
            "decreased": decreased,
        }
```

Create `backend/tests/test_sec_edgar.py`:
```python
"""
Tests for SEC EDGAR client.

File Name      : test_sec_edgar.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from datetime import datetime
from src.data.sec_edgar import SECEdgarClient, Filing13F, Holding


class TestSECEdgarClient:
    """Tests for SECEdgarClient."""
    
    @pytest.fixture
    def client(self):
        return SECEdgarClient()
    
    @pytest.fixture
    def sample_filing(self):
        return Filing13F(
            cik="0001067983",
            company_name="Berkshire Hathaway",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
                Holding(name="BANK OF AMER", cusip="060505104", value=30000000, shares=1000000000, share_type="SH"),
            ],
            total_value=180000000,
        )
    
    def test_compare_holdings_added(self, client, sample_filing):
        """Test detecting added positions."""
        previous = Filing13F(
            cik="0001067983",
            company_name="Berkshire Hathaway",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
            ],
            total_value=150000000,
        )
        
        changes = client.compare_holdings(sample_filing, previous)
        
        assert len(changes["added"]) == 1
        assert changes["added"][0].name == "BANK OF AMER"
        assert len(changes["removed"]) == 0
    
    def test_compare_holdings_removed(self, client, sample_filing):
        """Test detecting removed positions."""
        previous = Filing13F(
            cik="0001067983",
            company_name="Berkshire Hathaway",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
                Holding(name="BANK OF AMER", cusip="060505104", value=30000000, shares=1000000000, share_type="SH"),
                Holding(name="COCA-COLA", cusip="191216100", value=25000000, shares=400000000, share_type="SH"),
            ],
            total_value=205000000,
        )
        
        changes = client.compare_holdings(sample_filing, previous)
        
        assert len(changes["removed"]) == 1
        assert changes["removed"][0].name == "COCA-COLA"
    
    def test_compare_holdings_increased(self, client):
        """Test detecting increased positions."""
        current = Filing13F(
            cik="0001067983",
            company_name="Test",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=200000000, shares=1200000000, share_type="SH"),
            ],
            total_value=200000000,
        )
        previous = Filing13F(
            cik="0001067983",
            company_name="Test",
            filing_date=datetime.utcnow(),
            report_date=datetime.utcnow(),
            holdings=[
                Holding(name="APPLE INC", cusip="037833100", value=150000000, shares=900000000, share_type="SH"),
            ],
            total_value=150000000,
        )
        
        changes = client.compare_holdings(current, previous)
        
        assert len(changes["increased"]) == 1
        assert changes["increased"][0].shares == 1200000000
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_sec_edgar.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Holdings comparison logic correct
- [ ] XML parsing handles SEC format

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/1-1-data-fetchers

---

**Subtask 1.1.3: ARK Holdings Client (Single Session)**

**Prerequisites**:
- [x] 1.1.2: SEC EDGAR Client

**Deliverables**:
- [ ] `backend/src/data/ark_holdings.py` ARK daily holdings fetcher
- [ ] Parse CSV format from ARK website
- [ ] Track daily changes
- [ ] Unit tests

**Files to Create**:
- `backend/src/data/ark_holdings.py`
- `backend/tests/test_ark_holdings.py`

**Complete Code**:

Create `backend/src/data/ark_holdings.py`:
```python
"""
ARK Invest holdings data client.

File Name      : ark_holdings.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import requests
import pandas as pd
from io import StringIO
from datetime import datetime, date
from typing import Optional, Dict, List
from pydantic import BaseModel
from src.utils import get_logger

logger = get_logger(__name__)

ARK_HOLDINGS_URLS = {
    "ARKK": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv",
    "ARKW": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv",
    "ARKQ": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_AUTONOMOUS_TECH._&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv",
    "ARKG": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_GENOMIC_REVOLUTION_ETF_ARKG_HOLDINGS.csv",
    "ARKF": "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv",
}


class ARKHolding(BaseModel):
    """Single ARK ETF holding."""
    fund: str
    date: date
    company: str
    ticker: str
    cusip: str
    shares: float
    market_value: float
    weight: float  # Percentage of fund


class ARKDailySnapshot(BaseModel):
    """Daily snapshot of ARK holdings."""
    fund: str
    date: date
    holdings: List[ARKHolding]
    total_value: float


class ARKHoldingsClient:
    """Client for fetching ARK Invest daily holdings."""
    
    def __init__(self):
        self.session = requests.Session()
        self._cache: Dict[str, ARKDailySnapshot] = {}
    
    def get_holdings(self, fund: str = "ARKK") -> Optional[ARKDailySnapshot]:
        """
        Fetch current holdings for an ARK fund.
        
        Args:
            fund: Fund ticker (ARKK, ARKW, ARKQ, ARKG, ARKF)
            
        Returns:
            ARKDailySnapshot or None
        """
        fund = fund.upper()
        
        if fund not in ARK_HOLDINGS_URLS:
            logger.error(f"Unknown fund: {fund}")
            return None
        
        cache_key = f"{fund}_{date.today().isoformat()}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = ARK_HOLDINGS_URLS[fund]
            response = self.session.get(url)
            response.raise_for_status()
            
            df = pd.read_csv(StringIO(response.text))
            
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
            
            holdings = []
            for _, row in df.iterrows():
                if pd.isna(row.get("ticker")) or str(row.get("ticker")).strip() == "":
                    continue
                    
                holding = ARKHolding(
                    fund=fund,
                    date=date.today(),
                    company=str(row.get("company", "")).strip(),
                    ticker=str(row.get("ticker", "")).strip(),
                    cusip=str(row.get("cusip", "")).strip(),
                    shares=float(row.get("shares", 0)),
                    market_value=float(str(row.get("market_value_($)", 0)).replace(",", "").replace("$", "")),
                    weight=float(str(row.get("weight_(%)", 0)).replace("%", "")) / 100,
                )
                holdings.append(holding)
            
            total_value = sum(h.market_value for h in holdings)
            
            snapshot = ARKDailySnapshot(
                fund=fund,
                date=date.today(),
                holdings=holdings,
                total_value=total_value,
            )
            
            self._cache[cache_key] = snapshot
            logger.info(f"Fetched {len(holdings)} holdings for {fund}, total ${total_value:,.0f}")
            return snapshot
            
        except Exception as exc:
            logger.error(f"Error fetching {fund} holdings: {exc}")
            return None
    
    def get_top_holdings(self, fund: str = "ARKK", top_n: int = 10) -> List[ARKHolding]:
        """Get top N holdings by weight."""
        snapshot = self.get_holdings(fund)
        if not snapshot:
            return []
        
        sorted_holdings = sorted(snapshot.holdings, key=lambda h: h.weight, reverse=True)
        return sorted_holdings[:top_n]
    
    def compare_holdings(
        self,
        current: ARKDailySnapshot,
        previous: ARKDailySnapshot
    ) -> Dict[str, List[ARKHolding]]:
        """
        Compare two snapshots to find changes.
        
        Returns:
            Dict with 'added', 'removed', 'increased', 'decreased' keys
        """
        current_tickers = {h.ticker: h for h in current.holdings}
        previous_tickers = {h.ticker: h for h in previous.holdings}
        
        added = [h for t, h in current_tickers.items() if t not in previous_tickers]
        removed = [h for t, h in previous_tickers.items() if t not in current_tickers]
        
        increased = []
        decreased = []
        
        for ticker, current_holding in current_tickers.items():
            if ticker in previous_tickers:
                prev_shares = previous_tickers[ticker].shares
                if current_holding.shares > prev_shares * 1.01:
                    increased.append(current_holding)
                elif current_holding.shares < prev_shares * 0.99:
                    decreased.append(current_holding)
        
        return {
            "added": added,
            "removed": removed,
            "increased": increased,
            "decreased": decreased,
        }
```

Create `backend/tests/test_ark_holdings.py`:
```python
"""
Tests for ARK Holdings client.

File Name      : test_ark_holdings.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from datetime import date
from src.data.ark_holdings import ARKHoldingsClient, ARKDailySnapshot, ARKHolding


class TestARKHoldingsClient:
    """Tests for ARKHoldingsClient."""
    
    @pytest.fixture
    def client(self):
        return ARKHoldingsClient()
    
    @pytest.fixture
    def sample_snapshot(self):
        return ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1000000, market_value=200000000, weight=0.10),
                ARKHolding(fund="ARKK", date=date.today(), company="Roku Inc", ticker="ROKU", cusip="77543R102", shares=500000, market_value=50000000, weight=0.05),
            ],
            total_value=250000000,
        )
    
    def test_compare_holdings_added(self, client, sample_snapshot):
        """Test detecting added positions."""
        previous = ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1000000, market_value=200000000, weight=0.10),
            ],
            total_value=200000000,
        )
        
        changes = client.compare_holdings(sample_snapshot, previous)
        
        assert len(changes["added"]) == 1
        assert changes["added"][0].ticker == "ROKU"
    
    def test_compare_holdings_increased(self, client):
        """Test detecting increased positions."""
        current = ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1100000, market_value=220000000, weight=0.11),
            ],
            total_value=220000000,
        )
        previous = ARKDailySnapshot(
            fund="ARKK",
            date=date.today(),
            holdings=[
                ARKHolding(fund="ARKK", date=date.today(), company="Tesla Inc", ticker="TSLA", cusip="88160R101", shares=1000000, market_value=200000000, weight=0.10),
            ],
            total_value=200000000,
        )
        
        changes = client.compare_holdings(current, previous)
        
        assert len(changes["increased"]) == 1
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_ark_holdings.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] CSV parsing handles ARK format
- [ ] Change detection works

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/1-1-data-fetchers

---

**Subtask 1.1.4: FRED Macro Data Client (Single Session)**

**Prerequisites**:
- [x] 1.1.3: ARK Holdings Client

**Deliverables**:
- [ ] `backend/src/data/fred_client.py` Federal Reserve data fetcher
- [ ] Key macro indicators (GDP, inflation, rates, yields)
- [ ] Unit tests

**Files to Create**:
- `backend/src/data/fred_client.py`
- `backend/tests/test_fred_client.py`

**Complete Code**:

Create `backend/src/data/fred_client.py`:
```python
"""
FRED (Federal Reserve Economic Data) client.

File Name      : fred_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import requests
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel
from src.utils import get_logger, settings

logger = get_logger(__name__)

FRED_BASE_URL = "https://api.stlouisfed.org/fred"

MACRO_SERIES = {
    "GDP": "GDP",  # Gross Domestic Product
    "UNRATE": "UNRATE",  # Unemployment Rate
    "CPIAUCSL": "CPIAUCSL",  # Consumer Price Index
    "FEDFUNDS": "FEDFUNDS",  # Federal Funds Rate
    "DGS10": "DGS10",  # 10-Year Treasury Yield
    "DGS2": "DGS2",  # 2-Year Treasury Yield
    "T10Y2Y": "T10Y2Y",  # 10Y-2Y Spread (yield curve)
    "VIXCLS": "VIXCLS",  # VIX
    "DCOILWTICO": "DCOILWTICO",  # WTI Crude Oil
    "GOLDPMGBD228NLBM": "GOLDPMGBD228NLBM",  # Gold Price
}


class MacroDataPoint(BaseModel):
    """Single macro data point."""
    series_id: str
    date: date
    value: float


class MacroSnapshot(BaseModel):
    """Snapshot of macro economic indicators."""
    timestamp: datetime
    gdp_growth: Optional[float] = None
    unemployment: Optional[float] = None
    cpi_inflation: Optional[float] = None
    fed_funds_rate: Optional[float] = None
    treasury_10y: Optional[float] = None
    treasury_2y: Optional[float] = None
    yield_curve_spread: Optional[float] = None
    vix: Optional[float] = None
    oil_price: Optional[float] = None
    gold_price: Optional[float] = None


class FREDClient:
    """Client for fetching Federal Reserve economic data."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.fred_api_key
        self.session = requests.Session()
        self._cache: Dict[str, List[MacroDataPoint]] = {}
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MacroDataPoint]:
        """
        Fetch a data series from FRED.
        
        Args:
            series_id: FRED series identifier
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            List of MacroDataPoint
        """
        if not self.api_key:
            logger.warning("No FRED API key configured, returning empty data")
            return []
        
        if start_date is None:
            start_date = date.today() - timedelta(days=365)
        if end_date is None:
            end_date = date.today()
        
        cache_key = f"{series_id}_{start_date}_{end_date}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"{FRED_BASE_URL}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start_date.isoformat(),
                "observation_end": end_date.isoformat(),
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get("observations", [])
            
            points = []
            for obs in observations:
                if obs.get("value") != ".":
                    points.append(MacroDataPoint(
                        series_id=series_id,
                        date=datetime.strptime(obs["date"], "%Y-%m-%d").date(),
                        value=float(obs["value"]),
                    ))
            
            self._cache[cache_key] = points
            logger.info(f"Fetched {len(points)} observations for {series_id}")
            return points
            
        except Exception as exc:
            logger.error(f"Error fetching FRED series {series_id}: {exc}")
            return []
    
    def get_latest(self, series_id: str) -> Optional[MacroDataPoint]:
        """Get the most recent data point for a series."""
        points = self.get_series(series_id)
        return points[-1] if points else None
    
    def get_macro_snapshot(self) -> MacroSnapshot:
        """
        Get current snapshot of key macro indicators.
        
        Returns:
            MacroSnapshot with latest values
        """
        snapshot = MacroSnapshot(timestamp=datetime.utcnow())
        
        series_mapping = {
            "UNRATE": "unemployment",
            "CPIAUCSL": "cpi_inflation",
            "FEDFUNDS": "fed_funds_rate",
            "DGS10": "treasury_10y",
            "DGS2": "treasury_2y",
            "T10Y2Y": "yield_curve_spread",
            "VIXCLS": "vix",
            "DCOILWTICO": "oil_price",
            "GOLDPMGBD228NLBM": "gold_price",
        }
        
        for series_id, attr_name in series_mapping.items():
            latest = self.get_latest(series_id)
            if latest:
                setattr(snapshot, attr_name, latest.value)
        
        return snapshot
    
    def is_yield_curve_inverted(self) -> bool:
        """Check if the yield curve is inverted (2Y > 10Y)."""
        spread = self.get_latest("T10Y2Y")
        if spread:
            return spread.value < 0
        return False
```

Create `backend/tests/test_fred_client.py`:
```python
"""
Tests for FRED client.

File Name      : test_fred_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from src.data.fred_client import FREDClient, MacroDataPoint


class TestFREDClient:
    """Tests for FREDClient."""
    
    @pytest.fixture
    def client(self):
        return FREDClient(api_key="test_key")
    
    @pytest.fixture
    def mock_fred_response(self):
        return {
            "observations": [
                {"date": "2024-01-01", "value": "3.5"},
                {"date": "2024-02-01", "value": "3.4"},
                {"date": "2024-03-01", "value": "."},  # Missing data
                {"date": "2024-04-01", "value": "3.6"},
            ]
        }
    
    def test_get_series_success(self, client, mock_fred_response):
        """Test successful series fetch."""
        with patch.object(client.session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_fred_response
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            result = client.get_series("UNRATE")
            
            assert len(result) == 3  # Excludes missing "." value
            assert result[0].value == 3.5
            assert result[-1].value == 3.6
    
    def test_get_latest(self, client, mock_fred_response):
        """Test getting latest value."""
        with patch.object(client.session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_fred_response
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            result = client.get_latest("UNRATE")
            
            assert result is not None
            assert result.value == 3.6
    
    def test_no_api_key(self):
        """Test behavior without API key."""
        client = FREDClient(api_key=None)
        result = client.get_series("UNRATE")
        assert result == []
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_fred_client.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Handles missing data points
- [ ] Caching works

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/1-1-data-fetchers

---

### Task 1.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/1-1-data-fetchers`
- [ ] Delete branch: `git branch -d feature/1-1-data-fetchers`

---

### Task 1.2: Database Layer

**Subtask 1.2.1: DynamoDB Models and Access Layer (Single Session)**

**Prerequisites**:
- [x] 1.1.4: FRED Macro Data Client

**Deliverables**:
- [ ] `backend/src/db/__init__.py` module init
- [ ] `backend/src/db/dynamo.py` DynamoDB access layer
- [ ] Single-table design with GSI
- [ ] Models for users, portfolios, transactions, agent_runs
- [ ] Unit tests with moto

**Files to Create**:
- `backend/src/db/__init__.py`
- `backend/src/db/dynamo.py`
- `backend/src/db/models.py`
- `backend/tests/test_dynamo.py`

**Complete Code**:

Create `backend/src/db/__init__.py`:
```python
"""Database access layer for Council."""
from .dynamo import DynamoDBClient
from .models import User, Portfolio, Position, Transaction, AgentRun

__all__ = ["DynamoDBClient", "User", "Portfolio", "Position", "Transaction", "AgentRun"]
```

Create `backend/src/db/models.py`:
```python
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
        return {
            "pk": f"USER#{self.user_id}",
            "sk": f"PORTFOLIO#{self.agent_type.value}",
            "portfolio_id": self.portfolio_id,
            "user_id": self.user_id,
            "agent_type": self.agent_type.value,
            "cash": str(self.cash),
            "positions": [p.model_dump() for p in self.positions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "gsi1pk": f"AGENT#{self.agent_type.value}",
            "gsi1sk": f"USER#{self.user_id}",
        }
    
    @classmethod
    def from_dynamo(cls, item: Dict[str, Any]) -> "Portfolio":
        return cls(
            portfolio_id=item["portfolio_id"],
            user_id=item["user_id"],
            agent_type=AgentType(item["agent_type"]),
            cash=float(item["cash"]),
            positions=[Position(**p) for p in item.get("positions", [])],
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
```

Create `backend/src/db/dynamo.py`:
```python
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
```

Create `backend/tests/test_dynamo.py`:
```python
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
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_dynamo.py -v
```

**Success Criteria**:
- [ ] All tests pass with moto mocks
- [ ] Single-table design works correctly
- [ ] GSI queries function properly

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/1-2-database

---

### Task 1.2 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/1-2-database`
- [ ] Delete branch: `git branch -d feature/1-2-database`

---

## Phase 2: Agent Implementation

### Task 2.1: Base Agent and Simple Agents

**Subtask 2.1.1: Base Agent Class (Single Session)**

**Prerequisites**:
- [x] 1.2.1: DynamoDB Models and Access Layer

**Deliverables**:
- [ ] `backend/src/agents/__init__.py` module init
- [ ] `backend/src/agents/base.py` abstract base agent
- [ ] Common interface for all agents
- [ ] Portfolio management methods
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/__init__.py`
- `backend/src/agents/base.py`
- `backend/tests/test_base_agent.py`

**Complete Code**:

Create `backend/src/agents/__init__.py`:
```python
"""Investment agent implementations."""
from .base import BaseAgent
from .bogle import BogleAgent
from .buffett import BuffettAgent
from .graham import GrahamAgent
from .lynch import LynchAgent
from .dalio import DalioAgent
from .wood import WoodAgent

__all__ = [
    "BaseAgent",
    "BogleAgent",
    "BuffettAgent", 
    "GrahamAgent",
    "LynchAgent",
    "DalioAgent",
    "WoodAgent",
]
```

Create `backend/src/agents/base.py`:
```python
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
```

Create `backend/tests/test_base_agent.py`:
```python
"""
Tests for base agent class.

File Name      : test_base_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock, patch
from src.agents.base import BaseAgent, TradeRecommendation
from src.db.models import AgentType, TransactionType, Portfolio, Position


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""
    agent_type = AgentType.BUFFETT
    agent_name = "Test Agent"
    description = "Test agent implementation"
    
    def analyze_market(self) -> str:
        return "Market looks good"
    
    def generate_recommendations(self, portfolio: Portfolio):
        return [
            TradeRecommendation(
                action=TransactionType.BUY,
                symbol="AAPL",
                shares=10,
                reasoning="Test buy",
                confidence=0.8,
            )
        ]


class TestBaseAgent:
    """Tests for BaseAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        mock.get_fundamentals.return_value = MagicMock(price=175.0)
        return mock
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return ConcreteAgent(db_client=mock_db, data_client=mock_data)
    
    @pytest.fixture
    def sample_portfolio(self):
        return Portfolio(
            portfolio_id="test-port",
            user_id="test-user",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[],
        )
    
    def test_execute_buy_trade(self, agent, mock_db, mock_data, sample_portfolio):
        """Test executing a buy trade."""
        recommendation = TradeRecommendation(
            action=TransactionType.BUY,
            symbol="AAPL",
            shares=10,
            reasoning="Test buy",
            confidence=0.8,
        )
        
        txn = agent._execute_trade(sample_portfolio, recommendation)
        
        assert txn is not None
        assert txn.symbol == "AAPL"
        assert txn.shares == 10
        assert sample_portfolio.cash == 100000 - (175 * 10)
        assert len(sample_portfolio.positions) == 1
    
    def test_execute_sell_trade(self, agent, mock_db, mock_data, sample_portfolio):
        """Test executing a sell trade."""
        sample_portfolio.positions.append(
            Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
        )
        
        recommendation = TradeRecommendation(
            action=TransactionType.SELL,
            symbol="AAPL",
            shares=50,
            reasoning="Test sell",
            confidence=0.9,
        )
        
        txn = agent._execute_trade(sample_portfolio, recommendation)
        
        assert txn is not None
        assert sample_portfolio.positions[0].shares == 50
        assert sample_portfolio.cash == 100000 + (175 * 50)
    
    def test_insufficient_cash(self, agent, mock_db, mock_data, sample_portfolio):
        """Test handling insufficient cash for buy."""
        sample_portfolio.cash = 100  # Very low
        
        recommendation = TradeRecommendation(
            action=TransactionType.BUY,
            symbol="AAPL",
            shares=1000,
            reasoning="Test buy",
            confidence=0.8,
        )
        
        txn = agent._execute_trade(sample_portfolio, recommendation)
        
        # Should buy what we can afford (0 shares at $175)
        assert txn is None
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_base_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Trade execution handles edge cases
- [ ] Portfolio updates correctly

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-1-agents-base

---

**Subtask 2.1.2: Bogle Agent (Simplest) (Single Session)**

**Prerequisites**:
- [x] 2.1.1: Base Agent Class

**Deliverables**:
- [ ] `backend/src/agents/bogle.py` passive index agent
- [ ] Calendar-based investing logic
- [ ] Age-based allocation (mocked for now)
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/bogle.py`
- `backend/tests/test_bogle_agent.py`

**Complete Code**:

Create `backend/src/agents/bogle.py`:
```python
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
```

Create `backend/tests/test_bogle_agent.py`:
```python
"""
Tests for Bogle agent.

File Name      : test_bogle_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from datetime import date
from src.agents.bogle import BogleAgent, VTI, BND
from src.db.models import AgentType, Portfolio, Position


class TestBogleAgent:
    """Tests for BogleAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        mock.get_fundamentals.side_effect = lambda sym: MagicMock(
            price=250.0 if sym == VTI else 75.0
        )
        return mock
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return BogleAgent(db_client=mock_db, data_client=mock_data)
    
    @pytest.fixture
    def empty_portfolio(self):
        return Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BOGLE,
            cash=100000.0,
            positions=[],
        )
    
    def test_analyze_market_philosophy(self, agent):
        """Test that analysis reflects passive philosophy."""
        analysis = agent.analyze_market()
        
        assert "time in the market" in analysis.lower()
        assert "70%" in analysis or "stocks" in analysis.lower()
    
    def test_allocate_new_cash(self, agent, empty_portfolio, monkeypatch):
        """Test cash allocation on first of month."""
        monkeypatch.setattr(
            "src.agents.bogle.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 1)})
        )
        
        recs = agent._allocate_cash(100000.0)
        
        assert len(recs) == 2
        symbols = [r.symbol for r in recs]
        assert VTI in symbols
        assert BND in symbols
    
    def test_rebalance_when_off_target(self, agent, mock_data):
        """Test rebalancing when significantly off target."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BOGLE,
            cash=1000.0,
            positions=[
                Position(symbol=VTI, shares=400, avg_cost=200.0, current_price=250.0),  # $100k
                Position(symbol=BND, shares=200, avg_cost=70.0, current_price=75.0),   # $15k
            ],
        )
        
        current_stock_pct = 100000 / 115000
        recs = agent._rebalance(portfolio, current_stock_pct)
        
        assert len(recs) >= 0
    
    def test_no_action_when_balanced(self, agent):
        """Test no recommendations when portfolio is balanced."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BOGLE,
            cash=100.0,  # Minimal cash
            positions=[
                Position(symbol=VTI, shares=280, avg_cost=200.0, current_price=250.0),  # $70k (70%)
                Position(symbol=BND, shares=400, avg_cost=70.0, current_price=75.0),   # $30k (30%)
            ],
        )
        
        recs = agent.generate_recommendations(portfolio)
        
        assert len(recs) == 0
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_bogle_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Agent correctly allocates to VTI/BND
- [ ] Rebalancing triggers appropriately

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-1-agents-base

---

### Task 2.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/2-1-agents-base`
- [ ] Delete branch: `git branch -d feature/2-1-agents-base`

---

### Task 2.2: Value Agents

**Subtask 2.2.1: Buffett Agent (Single Session)**

**Prerequisites**:
- [x] 2.1.2: Bogle Agent

**Deliverables**:
- [ ] `backend/src/agents/buffett.py` value investing agent
- [ ] Moat analysis logic
- [ ] Concentrated position management
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/buffett.py`
- `backend/tests/test_buffett_agent.py`

**Complete Code**:

Create `backend/src/agents/buffett.py`:
```python
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
```

Create `backend/tests/test_buffett_agent.py`:
```python
"""
Tests for Buffett agent.

File Name      : test_buffett_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.buffett import BuffettAgent
from src.db.models import AgentType, Portfolio, Position
from src.data.yfinance_client import StockFundamentals


class TestBuffettAgent:
    """Tests for BuffettAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        return mock
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return BuffettAgent(db_client=mock_db, data_client=mock_data)
    
    @pytest.fixture
    def quality_stock(self):
        return StockFundamentals(
            symbol="AAPL",
            price=175.0,
            pe_ratio=28.0,
            pb_ratio=45.0,
            return_on_equity=0.25,
            profit_margin=0.25,
            debt_to_equity=80.0,
            current_ratio=1.5,
            market_cap=2800000000000,
        )
    
    @pytest.fixture
    def poor_stock(self):
        return StockFundamentals(
            symbol="BAD",
            price=10.0,
            pe_ratio=50.0,
            pb_ratio=5.0,
            return_on_equity=0.05,
            profit_margin=0.02,
            debt_to_equity=300.0,
            current_ratio=0.8,
            market_cap=1000000000,
        )
    
    def test_has_moat_quality_company(self, agent, quality_stock):
        """Test moat detection for quality company."""
        assert agent._has_moat(quality_stock) is True
    
    def test_has_moat_poor_company(self, agent, poor_stock):
        """Test moat detection for poor company."""
        assert agent._has_moat(poor_stock) is False
    
    def test_buffett_score_quality(self, agent, quality_stock):
        """Test scoring for quality company."""
        score = agent._calculate_buffett_score(quality_stock)
        assert score >= 0.6
    
    def test_buffett_score_poor(self, agent, poor_stock):
        """Test scoring for poor company."""
        score = agent._calculate_buffett_score(poor_stock)
        assert score < 0.5
    
    def test_position_sizing(self, agent, quality_stock):
        """Test position size calculation."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[],
        )
        
        shares = agent._calculate_position_size(portfolio, quality_stock)
        
        position_value = shares * quality_stock.price
        assert position_value <= portfolio.cash * 0.5
        assert position_value <= portfolio.total_value * 0.15
    
    def test_no_buy_overvalued(self, agent, mock_data):
        """Test no buy recommendation for overvalued stocks."""
        overvalued = StockFundamentals(
            symbol="OVER",
            price=500.0,
            pe_ratio=100.0,
            return_on_equity=0.20,
            profit_margin=0.15,
            debt_to_equity=50.0,
        )
        
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.BUFFETT,
            cash=100000.0,
            positions=[],
        )
        
        assert agent._is_buy_candidate(overvalued, portfolio) is False
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_buffett_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Moat detection works correctly
- [ ] Scoring reflects value criteria
- [ ] Position sizing respects limits

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-2-agents-value

---

**Subtask 2.2.2: Graham Agent (Single Session)**

**Prerequisites**:
- [x] 2.2.1: Buffett Agent

**Deliverables**:
- [ ] `backend/src/agents/graham.py` deep value agent
- [ ] Quantitative screening criteria
- [ ] Margin of safety calculations
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/graham.py`
- `backend/tests/test_graham_agent.py`

**Complete Code**:

Create `backend/src/agents/graham.py`:
```python
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
```

Create `backend/tests/test_graham_agent.py`:
```python
"""
Tests for Graham agent.

File Name      : test_graham_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.graham import GrahamAgent
from src.db.models import AgentType, Portfolio, Position
from src.data.yfinance_client import StockFundamentals


class TestGrahamAgent:
    """Tests for GrahamAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        return MagicMock()
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return GrahamAgent(db_client=mock_db, data_client=mock_data)
    
    @pytest.fixture
    def graham_stock(self):
        """Stock that passes Graham screen."""
        return StockFundamentals(
            symbol="VALUE",
            price=50.0,
            pe_ratio=10.0,
            pb_ratio=1.2,
            current_ratio=2.5,
            debt_to_equity=30.0,
            earnings_growth=0.05,
        )
    
    @pytest.fixture
    def growth_stock(self):
        """Stock that fails Graham screen."""
        return StockFundamentals(
            symbol="GROWTH",
            price=500.0,
            pe_ratio=50.0,
            pb_ratio=15.0,
            current_ratio=1.2,
            debt_to_equity=150.0,
        )
    
    def test_passes_graham_screen_value(self, agent, graham_stock):
        """Test screen passes for value stock."""
        assert agent._passes_graham_screen(graham_stock) is True
    
    def test_fails_graham_screen_growth(self, agent, growth_stock):
        """Test screen fails for growth stock."""
        assert agent._passes_graham_screen(growth_stock) is False
    
    def test_intrinsic_value_calculation(self, agent, graham_stock):
        """Test intrinsic value calculation."""
        intrinsic = agent._calculate_intrinsic_value(graham_stock)
        
        eps = 50.0 / 10.0  # $5
        expected = eps * (8.5 + 2 * 5.0)  # g=5%
        
        assert intrinsic == pytest.approx(expected, rel=0.01)
    
    def test_margin_of_safety(self, agent, graham_stock):
        """Test margin of safety calculation."""
        intrinsic = 100.0
        graham_stock.price = 60.0
        
        margin = agent._calculate_margin_of_safety(graham_stock, intrinsic)
        
        assert margin == pytest.approx(0.4, rel=0.01)
    
    def test_position_size_respects_max(self, agent, graham_stock):
        """Test position sizing respects 5% max."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.GRAHAM,
            cash=100000.0,
            positions=[],
        )
        
        shares = agent._calculate_position_size(portfolio, graham_stock)
        position_value = shares * graham_stock.price
        
        assert position_value <= portfolio.total_value * 0.05 + graham_stock.price
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_graham_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Graham screen correctly filters stocks
- [ ] Intrinsic value formula matches Graham's
- [ ] Position sizing respects 5% limit

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-2-agents-value

---

### Task 2.2 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/2-2-agents-value`
- [ ] Delete branch: `git branch -d feature/2-2-agents-value`

---

### Task 2.3: Growth and Macro Agents

**Subtask 2.3.1: Lynch Agent (Single Session)**

**Prerequisites**:
- [x] 2.2.2: Graham Agent

**Deliverables**:
- [ ] `backend/src/agents/lynch.py` GARP agent
- [ ] PEG ratio calculations
- [ ] Stock classification (slow grower, stalwart, fast grower, etc.)
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/lynch.py`
- `backend/tests/test_lynch_agent.py`

**Complete Code**:

Create `backend/src/agents/lynch.py`:
```python
"""
Peter Lynch Agent - Growth at a Reasonable Price.

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
```

Create `backend/tests/test_lynch_agent.py`:
```python
"""
Tests for Lynch agent.

File Name      : test_lynch_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.lynch import LynchAgent, StockCategory
from src.db.models import AgentType, Portfolio
from src.data.yfinance_client import StockFundamentals


class TestLynchAgent:
    """Tests for LynchAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        return MagicMock()
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return LynchAgent(db_client=mock_db, data_client=mock_data)
    
    def test_peg_calculation(self, agent):
        """Test PEG ratio calculation."""
        data = StockFundamentals(
            symbol="TEST",
            price=100.0,
            pe_ratio=20.0,
            earnings_growth=0.20,  # 20%
        )
        
        peg = agent._calculate_peg(data)
        
        assert peg == pytest.approx(1.0, rel=0.01)
    
    def test_classify_fast_grower(self, agent):
        """Test fast grower classification."""
        data = StockFundamentals(
            symbol="FAST",
            price=100.0,
            earnings_growth=0.25,  # 25%
        )
        
        category = agent._classify_stock(data)
        
        assert category == StockCategory.FAST_GROWER
    
    def test_classify_stalwart(self, agent):
        """Test stalwart classification."""
        data = StockFundamentals(
            symbol="STEADY",
            price=100.0,
            earnings_growth=0.12,  # 12%
        )
        
        category = agent._classify_stock(data)
        
        assert category == StockCategory.STALWART
    
    def test_classify_slow_grower(self, agent):
        """Test slow grower classification."""
        data = StockFundamentals(
            symbol="SLOW",
            price=100.0,
            earnings_growth=0.03,  # 3%
        )
        
        category = agent._classify_stock(data)
        
        assert category == StockCategory.SLOW_GROWER
    
    def test_no_peg_without_growth(self, agent):
        """Test PEG returns None without growth data."""
        data = StockFundamentals(
            symbol="NOGROW",
            price=100.0,
            pe_ratio=20.0,
            earnings_growth=None,
        )
        
        peg = agent._calculate_peg(data)
        
        assert peg is None
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_lynch_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] PEG calculation correct
- [ ] Stock classification works

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-3-agents-growth

---

**Subtask 2.3.2: Dalio Agent (Single Session)**

**Prerequisites**:
- [x] 2.3.1: Lynch Agent

**Deliverables**:
- [ ] `backend/src/agents/dalio.py` all-weather agent
- [ ] Macro indicator analysis
- [ ] Risk parity allocation
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/dalio.py`
- `backend/tests/test_dalio_agent.py`

**Complete Code**:

Create `backend/src/agents/dalio.py`:
```python
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
```

Create `backend/tests/test_dalio_agent.py`:
```python
"""
Tests for Dalio agent.

File Name      : test_dalio_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.dalio import DalioAgent, ALL_WEATHER_ALLOCATION
from src.db.models import AgentType, Portfolio, Position


class TestDalioAgent:
    """Tests for DalioAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        mock = MagicMock()
        mock.get_fundamentals.side_effect = lambda sym: MagicMock(price=100.0)
        return mock
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return DalioAgent(db_client=mock_db, data_client=mock_data)
    
    def test_allocation_sums_to_one(self):
        """Test all-weather allocation sums to 100%."""
        total = sum(ALL_WEATHER_ALLOCATION.values())
        assert total == pytest.approx(1.0, rel=0.01)
    
    def test_calculate_current_allocation(self, agent):
        """Test current allocation calculation."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.DALIO,
            cash=10000.0,
            positions=[
                Position(symbol="VTI", shares=300, avg_cost=90.0, current_price=100.0),
                Position(symbol="TLT", shares=400, avg_cost=95.0, current_price=100.0),
            ],
        )
        
        allocation = agent._calculate_current_allocation(portfolio)
        
        total = portfolio.total_value
        assert allocation["VTI"] == pytest.approx(30000 / total, rel=0.01)
        assert allocation["TLT"] == pytest.approx(40000 / total, rel=0.01)
    
    def test_deploy_cash_all_assets(self, agent, mock_data):
        """Test cash deployment covers all assets."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.DALIO,
            cash=100000.0,
            positions=[],
        )
        
        recommendations = agent._deploy_cash(portfolio)
        
        symbols = {r.symbol for r in recommendations}
        assert symbols == set(ALL_WEATHER_ALLOCATION.keys())
    
    def test_rebalance_triggers_on_drift(self, agent, mock_data):
        """Test rebalancing triggers when drift exceeds threshold."""
        portfolio = Portfolio(
            portfolio_id="test",
            user_id="user1",
            agent_type=AgentType.DALIO,
            cash=5000.0,
            positions=[
                Position(symbol="VTI", shares=450, avg_cost=90.0, current_price=100.0),
                Position(symbol="TLT", shares=350, avg_cost=95.0, current_price=100.0),
                Position(symbol="IEI", shares=100, avg_cost=95.0, current_price=100.0),
                Position(symbol="GLD", shares=50, avg_cost=180.0, current_price=100.0),
                Position(symbol="DBC", shares=50, avg_cost=20.0, current_price=100.0),
            ],
        )
        
        recommendations = agent.generate_recommendations(portfolio)
        
        assert len(recommendations) >= 0
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_dalio_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] All-weather allocation correct
- [ ] Rebalancing logic works

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-3-agents-growth

---

**Subtask 2.3.3: Wood Agent (Single Session)**

**Prerequisites**:
- [x] 2.3.2: Dalio Agent

**Deliverables**:
- [ ] `backend/src/agents/wood.py` disruptive innovation agent
- [ ] Theme-based analysis
- [ ] High-conviction positions
- [ ] Unit tests

**Files to Create**:
- `backend/src/agents/wood.py`
- `backend/tests/test_wood_agent.py`

**Complete Code**:

Create `backend/src/agents/wood.py`:
```python
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
```

Create `backend/tests/test_wood_agent.py`:
```python
"""
Tests for Wood agent.

File Name      : test_wood_agent.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock
from src.agents.wood import WoodAgent, InnovationTheme, THEME_STOCKS
from src.db.models import AgentType, Portfolio, Position
from src.data.yfinance_client import StockFundamentals


class TestWoodAgent:
    """Tests for WoodAgent."""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data(self):
        return MagicMock()
    
    @pytest.fixture
    def agent(self, mock_db, mock_data):
        return WoodAgent(db_client=mock_db, data_client=mock_data)
    
    def test_themes_have_stocks(self):
        """Test all themes have stocks assigned."""
        for theme in InnovationTheme:
            assert theme in THEME_STOCKS
            assert len(THEME_STOCKS[theme]) > 0
    
    def test_innovation_score_high_growth(self, agent):
        """Test high score for high growth stock."""
        data = StockFundamentals(
            symbol="GROWTH",
            price=100.0,
            revenue_growth=0.40,
            market_cap=5_000_000_000,
            beta=1.8,
        )
        
        score = agent._calculate_innovation_score(data)
        
        assert score > 0.7
    
    def test_innovation_score_low_growth(self, agent):
        """Test low score for low growth stock."""
        data = StockFundamentals(
            symbol="SLOW",
            price=100.0,
            revenue_growth=0.02,
            market_cap=500_000_000_000,
            beta=0.8,
        )
        
        score = agent._calculate_innovation_score(data)
        
        assert score < 0.5
    
    def test_get_stock_themes(self, agent):
        """Test getting themes for a stock."""
        themes = agent._get_stock_themes("TSLA")
        
        assert InnovationTheme.ENERGY in themes or InnovationTheme.MOBILITY in themes
    
    def test_buy_the_dip_detection(self, agent):
        """Test buy-the-dip detection."""
        data = StockFundamentals(
            symbol="DIP",
            price=70.0,
            fifty_two_week_high=120.0,
        )
        
        position = Position(
            symbol="DIP",
            shares=100,
            avg_cost=100.0,
            current_price=70.0,
        )
        
        assert agent._is_buy_the_dip(data, position) is True
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_wood_agent.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Innovation scoring works
- [ ] Theme mapping correct

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/2-3-agents-growth

---

### Task 2.3 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/2-3-agents-growth`
- [ ] Delete branch: `git branch -d feature/2-3-agents-growth`

---

## Phase 3: API and Scheduler

### Task 3.1: Lambda API Handlers

**Subtask 3.1.1: Dashboard API (Single Session)**

**Prerequisites**:
- [x] 2.3.3: Wood Agent

**Deliverables**:
- [ ] `backend/src/api/__init__.py` module init
- [ ] `backend/src/api/dashboard.py` dashboard Lambda handler
- [ ] Get all agents summary, latest runs, portfolio overview
- [ ] Unit tests

**Files to Create**:
- `backend/src/api/__init__.py`
- `backend/src/api/dashboard.py`
- `backend/tests/test_api_dashboard.py`

**Complete Code**:

Create `backend/src/api/__init__.py`:
```python
"""API Lambda handlers for Council."""
```

Create `backend/src/api/dashboard.py`:
```python
"""
Dashboard API Lambda handler.

File Name      : dashboard.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
from typing import Dict, Any
from datetime import datetime

from src.db import DynamoDBClient
from src.db.models import AgentType
from src.utils import get_logger

logger = get_logger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for dashboard endpoints.
    
    Routes:
    - GET /dashboard - Get overview of all agents
    - GET /agents/{agent_id} - Get agent details
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}
    
    user_id = _get_user_id(event)
    if not user_id:
        return _response(401, {"error": "Unauthorized"})
    
    try:
        db = DynamoDBClient()
        
        if path == "/dashboard" and http_method == "GET":
            return _get_dashboard(db, user_id)
        
        elif "/agents/" in path and http_method == "GET":
            agent_id = path_params.get("agent_id")
            return _get_agent_detail(db, user_id, agent_id)
        
        return _response(404, {"error": "Not found"})
        
    except Exception as exc:
        logger.error(f"Dashboard error: {exc}")
        return _response(500, {"error": str(exc)})


def _get_dashboard(db: DynamoDBClient, user_id: str) -> Dict[str, Any]:
    """Get dashboard overview."""
    agents_summary = []
    
    for agent_type in AgentType:
        portfolio = db.get_portfolio(user_id, agent_type)
        latest_run = db.get_latest_agent_run(agent_type)
        
        summary = {
            "agent_type": agent_type.value,
            "agent_name": _get_agent_name(agent_type),
            "portfolio_value": portfolio.total_value if portfolio else 0,
            "cash": portfolio.cash if portfolio else 0,
            "num_positions": len(portfolio.positions) if portfolio else 0,
            "last_run": latest_run.run_date.isoformat() if latest_run else None,
            "last_analysis": latest_run.analysis[:200] if latest_run else None,
        }
        agents_summary.append(summary)
    
    total_value = sum(a["portfolio_value"] for a in agents_summary)
    
    return _response(200, {
        "user_id": user_id,
        "total_value": total_value,
        "agents": agents_summary,
        "generated_at": datetime.utcnow().isoformat(),
    })


def _get_agent_detail(
    db: DynamoDBClient,
    user_id: str,
    agent_id: str
) -> Dict[str, Any]:
    """Get detailed view of a single agent."""
    try:
        agent_type = AgentType(agent_id)
    except ValueError:
        return _response(400, {"error": f"Invalid agent: {agent_id}"})
    
    portfolio = db.get_portfolio(user_id, agent_type)
    runs = db.get_agent_runs(agent_type, limit=10)
    transactions = db.get_user_transactions(user_id, limit=20)
    agent_txns = [t for t in transactions if t.agent_type == agent_type]
    
    positions = []
    if portfolio:
        for pos in portfolio.positions:
            positions.append({
                "symbol": pos.symbol,
                "shares": pos.shares,
                "avg_cost": pos.avg_cost,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "gain_loss": pos.gain_loss,
                "gain_loss_pct": pos.gain_loss_pct * 100,
            })
    
    return _response(200, {
        "agent_type": agent_type.value,
        "agent_name": _get_agent_name(agent_type),
        "portfolio": {
            "total_value": portfolio.total_value if portfolio else 0,
            "cash": portfolio.cash if portfolio else 0,
            "positions": positions,
        },
        "recent_runs": [
            {
                "run_id": r.run_id,
                "date": r.run_date.isoformat(),
                "analysis": r.analysis,
                "recommendations": r.recommendations,
                "trades_executed": len(r.executed_trades),
                "value_before": r.portfolio_value_before,
                "value_after": r.portfolio_value_after,
            }
            for r in runs
        ],
        "recent_transactions": [
            {
                "transaction_id": t.transaction_id,
                "type": t.transaction_type.value,
                "symbol": t.symbol,
                "shares": t.shares,
                "price": t.price,
                "reasoning": t.reasoning,
                "date": t.created_at.isoformat(),
            }
            for t in agent_txns[:10]
        ],
    })


def _get_agent_name(agent_type: AgentType) -> str:
    """Get display name for agent."""
    names = {
        AgentType.BUFFETT: "Warren Buffett",
        AgentType.GRAHAM: "Benjamin Graham",
        AgentType.LYNCH: "Peter Lynch",
        AgentType.DALIO: "Ray Dalio",
        AgentType.BOGLE: "John Bogle",
        AgentType.WOOD: "Cathie Wood",
    }
    return names.get(agent_type, agent_type.value)


def _get_user_id(event: Dict[str, Any]) -> str:
    """Extract user ID from Cognito authorizer."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub", "")


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Build API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }
```

Create `backend/tests/test_api_dashboard.py`:
```python
"""
Tests for Dashboard API.

File Name      : test_api_dashboard.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.api.dashboard import handler, _get_agent_name
from src.db.models import AgentType, Portfolio, Position, AgentRun


class TestDashboardAPI:
    """Tests for Dashboard API."""
    
    @pytest.fixture
    def mock_event(self):
        return {
            "httpMethod": "GET",
            "path": "/dashboard",
            "pathParameters": None,
            "requestContext": {
                "authorizer": {
                    "claims": {"sub": "user123"}
                }
            }
        }
    
    @pytest.fixture
    def mock_portfolio(self):
        return Portfolio(
            portfolio_id="port1",
            user_id="user123",
            agent_type=AgentType.BUFFETT,
            cash=50000.0,
            positions=[
                Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
            ],
        )
    
    def test_unauthorized_without_user(self):
        """Test 401 when no user in claims."""
        event = {
            "httpMethod": "GET",
            "path": "/dashboard",
            "requestContext": {"authorizer": {"claims": {}}}
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 401
    
    def test_get_dashboard_success(self, mock_event, mock_portfolio):
        """Test successful dashboard retrieval."""
        with patch("src.api.dashboard.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_portfolio.return_value = mock_portfolio
            mock_db.get_latest_agent_run.return_value = None
            mock_db_class.return_value = mock_db
            
            response = handler(mock_event, None)
            
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert "agents" in body
            assert len(body["agents"]) == 6
    
    def test_get_agent_detail(self, mock_portfolio):
        """Test agent detail endpoint."""
        event = {
            "httpMethod": "GET",
            "path": "/agents/buffett",
            "pathParameters": {"agent_id": "buffett"},
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }
        
        with patch("src.api.dashboard.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_portfolio.return_value = mock_portfolio
            mock_db.get_agent_runs.return_value = []
            mock_db.get_user_transactions.return_value = []
            mock_db_class.return_value = mock_db
            
            response = handler(event, None)
            
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["agent_type"] == "buffett"
    
    def test_get_agent_name(self):
        """Test agent name lookup."""
        assert _get_agent_name(AgentType.BUFFETT) == "Warren Buffett"
        assert _get_agent_name(AgentType.BOGLE) == "John Bogle"
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_api_dashboard.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Dashboard returns all 6 agents
- [ ] Agent detail returns portfolio and history

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/3-1-api

---

**Subtask 3.1.2: Portfolio API (Single Session)**

**Prerequisites**:
- [x] 3.1.1: Dashboard API

**Deliverables**:
- [ ] `backend/src/api/portfolios.py` portfolio Lambda handler
- [ ] CRUD operations for portfolios
- [ ] Unit tests

**Files to Create**:
- `backend/src/api/portfolios.py`
- `backend/tests/test_api_portfolios.py`

**Complete Code**:

Create `backend/src/api/portfolios.py`:
```python
"""
Portfolio API Lambda handler.

File Name      : portfolios.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
from typing import Dict, Any

from src.db import DynamoDBClient
from src.db.models import AgentType
from src.utils import get_logger

logger = get_logger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for portfolio endpoints.
    
    Routes:
    - GET /portfolios - List all user portfolios
    - GET /portfolios/{portfolio_id} - Get specific portfolio
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "")
    path_params = event.get("pathParameters") or {}
    
    user_id = _get_user_id(event)
    if not user_id:
        return _response(401, {"error": "Unauthorized"})
    
    try:
        db = DynamoDBClient()
        
        if path == "/portfolios" and http_method == "GET":
            return _list_portfolios(db, user_id)
        
        elif "/portfolios/" in path and http_method == "GET":
            portfolio_id = path_params.get("portfolio_id")
            return _get_portfolio(db, user_id, portfolio_id)
        
        return _response(404, {"error": "Not found"})
        
    except Exception as exc:
        logger.error(f"Portfolio error: {exc}")
        return _response(500, {"error": str(exc)})


def _list_portfolios(db: DynamoDBClient, user_id: str) -> Dict[str, Any]:
    """List all portfolios for user."""
    portfolios = db.get_user_portfolios(user_id)
    
    result = []
    for portfolio in portfolios:
        result.append({
            "portfolio_id": portfolio.portfolio_id,
            "agent_type": portfolio.agent_type.value,
            "total_value": portfolio.total_value,
            "cash": portfolio.cash,
            "num_positions": len(portfolio.positions),
            "updated_at": portfolio.updated_at.isoformat(),
        })
    
    return _response(200, {
        "portfolios": result,
        "total_count": len(result),
    })


def _get_portfolio(
    db: DynamoDBClient,
    user_id: str,
    portfolio_id: str
) -> Dict[str, Any]:
    """Get specific portfolio by ID."""
    portfolios = db.get_user_portfolios(user_id)
    portfolio = next(
        (p for p in portfolios if p.portfolio_id == portfolio_id),
        None
    )
    
    if not portfolio:
        return _response(404, {"error": "Portfolio not found"})
    
    positions = []
    for pos in portfolio.positions:
        positions.append({
            "symbol": pos.symbol,
            "shares": pos.shares,
            "avg_cost": pos.avg_cost,
            "current_price": pos.current_price,
            "market_value": pos.market_value,
            "gain_loss": pos.gain_loss,
            "gain_loss_pct": pos.gain_loss_pct * 100,
        })
    
    return _response(200, {
        "portfolio_id": portfolio.portfolio_id,
        "agent_type": portfolio.agent_type.value,
        "cash": portfolio.cash,
        "total_value": portfolio.total_value,
        "positions": positions,
        "created_at": portfolio.created_at.isoformat(),
        "updated_at": portfolio.updated_at.isoformat(),
    })


def _get_user_id(event: Dict[str, Any]) -> str:
    """Extract user ID from Cognito authorizer."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub", "")


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Build API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }
```

Create `backend/tests/test_api_portfolios.py`:
```python
"""
Tests for Portfolio API.

File Name      : test_api_portfolios.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
import json
from unittest.mock import MagicMock, patch

from src.api.portfolios import handler
from src.db.models import AgentType, Portfolio, Position


class TestPortfolioAPI:
    """Tests for Portfolio API."""
    
    @pytest.fixture
    def mock_portfolios(self):
        return [
            Portfolio(
                portfolio_id="port1",
                user_id="user123",
                agent_type=AgentType.BUFFETT,
                cash=50000.0,
                positions=[
                    Position(symbol="AAPL", shares=100, avg_cost=150.0, current_price=175.0)
                ],
            ),
            Portfolio(
                portfolio_id="port2",
                user_id="user123",
                agent_type=AgentType.BOGLE,
                cash=30000.0,
                positions=[],
            ),
        ]
    
    def test_list_portfolios(self, mock_portfolios):
        """Test listing all portfolios."""
        event = {
            "httpMethod": "GET",
            "path": "/portfolios",
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }
        
        with patch("src.api.portfolios.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user_portfolios.return_value = mock_portfolios
            mock_db_class.return_value = mock_db
            
            response = handler(event, None)
            
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert len(body["portfolios"]) == 2
    
    def test_get_portfolio_by_id(self, mock_portfolios):
        """Test getting specific portfolio."""
        event = {
            "httpMethod": "GET",
            "path": "/portfolios/port1",
            "pathParameters": {"portfolio_id": "port1"},
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }
        
        with patch("src.api.portfolios.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user_portfolios.return_value = mock_portfolios
            mock_db_class.return_value = mock_db
            
            response = handler(event, None)
            
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["portfolio_id"] == "port1"
    
    def test_portfolio_not_found(self, mock_portfolios):
        """Test 404 for unknown portfolio."""
        event = {
            "httpMethod": "GET",
            "path": "/portfolios/unknown",
            "pathParameters": {"portfolio_id": "unknown"},
            "requestContext": {
                "authorizer": {"claims": {"sub": "user123"}}
            }
        }
        
        with patch("src.api.portfolios.DynamoDBClient") as mock_db_class:
            mock_db = MagicMock()
            mock_db.get_user_portfolios.return_value = mock_portfolios
            mock_db_class.return_value = mock_db
            
            response = handler(event, None)
            
            assert response["statusCode"] == 404
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_api_portfolios.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Portfolio list works
- [ ] Portfolio detail works

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/3-1-api

---

### Task 3.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/3-1-api`
- [ ] Delete branch: `git branch -d feature/3-1-api`

---

### Task 3.2: Scheduler

**Subtask 3.2.1: Daily Run Orchestrator (Single Session)**

**Prerequisites**:
- [x] 3.1.2: Portfolio API

**Deliverables**:
- [ ] `backend/src/scheduler/__init__.py` module init
- [ ] `backend/src/scheduler/daily_run.py` orchestrator Lambda
- [ ] Run all 6 agents for all users
- [ ] Unit tests

**Files to Create**:
- `backend/src/scheduler/__init__.py`
- `backend/src/scheduler/daily_run.py`
- `backend/tests/test_scheduler.py`

**Complete Code**:

Create `backend/src/scheduler/__init__.py`:
```python
"""Scheduler modules for Council."""
```

Create `backend/src/scheduler/daily_run.py`:
```python
"""
Daily run orchestrator Lambda.

File Name      : daily_run.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import json
from typing import Dict, Any, List
from datetime import datetime, date
import traceback

from src.db import DynamoDBClient, User
from src.db.models import AgentType
from src.agents import (
    BuffettAgent, GrahamAgent, LynchAgent,
    DalioAgent, BogleAgent, WoodAgent
)
from src.alerts.ses_client import send_daily_summary
from src.utils import get_logger

logger = get_logger(__name__)

AGENT_CLASSES = {
    AgentType.BUFFETT: BuffettAgent,
    AgentType.GRAHAM: GrahamAgent,
    AgentType.LYNCH: LynchAgent,
    AgentType.DALIO: DalioAgent,
    AgentType.BOGLE: BogleAgent,
    AgentType.WOOD: WoodAgent,
}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for daily scheduled runs.
    
    Triggered by EventBridge at 9 AM EST on market days.
    Runs all 6 agents for all users.
    """
    logger.info("Starting daily agent runs")
    start_time = datetime.utcnow()
    
    if not _is_market_day():
        logger.info("Not a market day, skipping")
        return {"statusCode": 200, "body": "Market closed"}
    
    try:
        db = DynamoDBClient()
        users = _get_all_users(db)
        
        results = []
        for user in users:
            user_results = _run_agents_for_user(db, user)
            results.append({
                "user_id": user.user_id,
                "results": user_results,
            })
            
            if user.email_alerts_enabled:
                _send_user_summary(user, user_results)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Completed all runs in {duration:.1f}s")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "users_processed": len(users),
                "duration_seconds": duration,
                "results": results,
            })
        }
        
    except Exception as exc:
        logger.error(f"Daily run failed: {exc}\n{traceback.format_exc()}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)})
        }


def _is_market_day() -> bool:
    """Check if today is a market day (weekday)."""
    today = date.today()
    return today.weekday() < 5


def _get_all_users(db: DynamoDBClient) -> List[User]:
    """Get all users from database."""
    # In production, would scan/query users table
    # For MVP, return empty list (users created on first API call)
    return []


def _run_agents_for_user(
    db: DynamoDBClient,
    user: User
) -> List[Dict[str, Any]]:
    """Run all agents for a single user."""
    results = []
    
    for agent_type, agent_class in AGENT_CLASSES.items():
        try:
            agent = agent_class(db_client=db)
            run = agent.run(user.user_id)
            
            results.append({
                "agent": agent_type.value,
                "status": "success",
                "run_id": run.run_id,
                "trades": len(run.executed_trades),
                "value_change": run.portfolio_value_after - run.portfolio_value_before,
            })
            
        except Exception as exc:
            logger.error(f"Agent {agent_type.value} failed for {user.user_id}: {exc}")
            results.append({
                "agent": agent_type.value,
                "status": "error",
                "error": str(exc),
            })
    
    return results


def _send_user_summary(user: User, results: List[Dict[str, Any]]) -> None:
    """Send daily summary email to user."""
    try:
        trades_today = sum(r.get("trades", 0) for r in results if r["status"] == "success")
        if trades_today > 0:
            send_daily_summary(user.email, results)
    except Exception as exc:
        logger.error(f"Failed to send summary to {user.email}: {exc}")
```

Create `backend/tests/test_scheduler.py`:
```python
"""
Tests for scheduler.

File Name      : test_scheduler.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from src.scheduler.daily_run import handler, _is_market_day, _run_agents_for_user
from src.db.models import User


class TestScheduler:
    """Tests for daily scheduler."""
    
    def test_is_market_day_weekday(self, monkeypatch):
        """Test market day detection for weekday."""
        monkeypatch.setattr(
            "src.scheduler.daily_run.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 8)})  # Monday
        )
        assert _is_market_day() is True
    
    def test_is_market_day_weekend(self, monkeypatch):
        """Test market day detection for weekend."""
        monkeypatch.setattr(
            "src.scheduler.daily_run.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 6)})  # Saturday
        )
        assert _is_market_day() is False
    
    def test_run_agents_for_user(self):
        """Test running all agents for a user."""
        mock_db = MagicMock()
        mock_db.get_portfolio.return_value = None
        mock_db.save_portfolio.return_value = True
        mock_db.save_agent_run.return_value = True
        mock_db.save_transaction.return_value = True
        
        user = User(user_id="test123", email="test@example.com")
        
        with patch("src.scheduler.daily_run.AGENT_CLASSES") as mock_agents:
            mock_agent = MagicMock()
            mock_run = MagicMock()
            mock_run.run_id = "run123"
            mock_run.executed_trades = []
            mock_run.portfolio_value_before = 100000
            mock_run.portfolio_value_after = 100500
            mock_agent.return_value.run.return_value = mock_run
            
            mock_agents.items.return_value = [("buffett", mock_agent)]
            
            results = _run_agents_for_user(mock_db, user)
            
            assert len(results) == 1
            assert results[0]["status"] == "success"
    
    def test_handler_skips_weekend(self, monkeypatch):
        """Test handler skips on weekends."""
        monkeypatch.setattr(
            "src.scheduler.daily_run.date",
            type("MockDate", (), {"today": lambda: date(2024, 1, 6)})
        )
        
        response = handler({}, None)
        
        assert response["statusCode"] == 200
        assert "closed" in response["body"]
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_scheduler.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Market day detection works
- [ ] All agents run for each user

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/3-2-scheduler

---

### Task 3.2 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/3-2-scheduler`
- [ ] Delete branch: `git branch -d feature/3-2-scheduler`

---

## Phase 4: Email Alerts

### Task 4.1: SES Integration

**Subtask 4.1.1: Email Client and Templates (Single Session)**

**Prerequisites**:
- [x] 3.2.1: Daily Run Orchestrator

**Deliverables**:
- [ ] `backend/src/alerts/__init__.py` module init
- [ ] `backend/src/alerts/ses_client.py` SES email sender
- [ ] Email templates for daily summary and trade alerts
- [ ] Unit tests

**Files to Create**:
- `backend/src/alerts/__init__.py`
- `backend/src/alerts/ses_client.py`
- `backend/tests/test_ses_client.py`

**Complete Code**:

Create `backend/src/alerts/__init__.py`:
```python
"""Alert and notification modules for Council."""
from .ses_client import send_daily_summary, send_trade_alert

__all__ = ["send_daily_summary", "send_trade_alert"]
```

Create `backend/src/alerts/ses_client.py`:
```python
"""
AWS SES email client for alerts.

File Name      : ses_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import boto3
from typing import Dict, Any, List
from datetime import datetime

from src.utils import get_logger, settings

logger = get_logger(__name__)

DAILY_SUMMARY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
        .header {{ background: #1a365d; color: white; padding: 20px; text-align: center; }}
        .agent {{ border: 1px solid #e2e8f0; margin: 10px 0; padding: 15px; border-radius: 8px; }}
        .success {{ border-left: 4px solid #48bb78; }}
        .error {{ border-left: 4px solid #f56565; }}
        .trades {{ color: #2d3748; font-weight: bold; }}
        .value {{ color: #38a169; }}
        .footer {{ text-align: center; padding: 20px; color: #718096; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Council Daily Summary</h1>
        <p>{date}</p>
    </div>
    
    <div class="content">
        <h2>Agent Activity</h2>
        {agent_summaries}
    </div>
    
    <div class="footer">
        <p>You are receiving this because you enabled email alerts in Council.</p>
        <p>Manage preferences in your account settings.</p>
    </div>
</body>
</html>
"""

TRADE_ALERT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
        .header {{ background: #2c5282; color: white; padding: 20px; text-align: center; }}
        .trade {{ background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .buy {{ border-left: 4px solid #48bb78; }}
        .sell {{ border-left: 4px solid #ed8936; }}
        .symbol {{ font-size: 24px; font-weight: bold; }}
        .reasoning {{ color: #4a5568; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Trade Alert</h1>
        <p>{agent_name}</p>
    </div>
    
    <div class="trade {trade_type}">
        <div class="symbol">{trade_type_upper} {symbol}</div>
        <p><strong>Shares:</strong> {shares}</p>
        <p><strong>Price:</strong> ${price:.2f}</p>
        <p><strong>Total:</strong> ${total:.2f}</p>
        <div class="reasoning">
            <strong>Reasoning:</strong> {reasoning}
        </div>
    </div>
</body>
</html>
"""


def send_daily_summary(
    recipient: str,
    results: List[Dict[str, Any]]
) -> bool:
    """
    Send daily summary email.
    
    Args:
        recipient: Email address
        results: List of agent run results
        
    Returns:
        True if sent successfully
    """
    if not settings.ses_sender_email:
        logger.warning("SES sender email not configured")
        return False
    
    agent_html = ""
    for result in results:
        status_class = "success" if result["status"] == "success" else "error"
        
        if result["status"] == "success":
            agent_html += f"""
            <div class="agent {status_class}">
                <h3>{result['agent'].title()}</h3>
                <p class="trades">Trades executed: {result.get('trades', 0)}</p>
                <p class="value">Value change: ${result.get('value_change', 0):,.2f}</p>
            </div>
            """
        else:
            agent_html += f"""
            <div class="agent {status_class}">
                <h3>{result['agent'].title()}</h3>
                <p>Error: {result.get('error', 'Unknown error')}</p>
            </div>
            """
    
    html_body = DAILY_SUMMARY_TEMPLATE.format(
        date=datetime.utcnow().strftime("%B %d, %Y"),
        agent_summaries=agent_html,
    )
    
    return _send_email(
        recipient=recipient,
        subject=f"Council Daily Summary - {datetime.utcnow().strftime('%Y-%m-%d')}",
        html_body=html_body,
    )


def send_trade_alert(
    recipient: str,
    agent_name: str,
    trade_type: str,
    symbol: str,
    shares: float,
    price: float,
    reasoning: str
) -> bool:
    """
    Send trade alert email.
    
    Args:
        recipient: Email address
        agent_name: Name of agent making trade
        trade_type: "buy" or "sell"
        symbol: Stock symbol
        shares: Number of shares
        price: Price per share
        reasoning: Trade reasoning
        
    Returns:
        True if sent successfully
    """
    if not settings.ses_sender_email:
        logger.warning("SES sender email not configured")
        return False
    
    html_body = TRADE_ALERT_TEMPLATE.format(
        agent_name=agent_name,
        trade_type=trade_type.lower(),
        trade_type_upper=trade_type.upper(),
        symbol=symbol,
        shares=shares,
        price=price,
        total=shares * price,
        reasoning=reasoning,
    )
    
    return _send_email(
        recipient=recipient,
        subject=f"Council Trade Alert: {agent_name} {trade_type.upper()} {symbol}",
        html_body=html_body,
    )


def _send_email(
    recipient: str,
    subject: str,
    html_body: str
) -> bool:
    """Send email via SES."""
    try:
        ses = boto3.client("ses", region_name=settings.aws_region)
        
        response = ses.send_email(
            Source=settings.ses_sender_email,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_body}},
            },
        )
        
        logger.info(f"Email sent to {recipient}: {response['MessageId']}")
        return True
        
    except Exception as exc:
        logger.error(f"Failed to send email to {recipient}: {exc}")
        return False
```

Create `backend/tests/test_ses_client.py`:
```python
"""
Tests for SES client.

File Name      : test_ses_client.py
Author         : Mike Morris
Prerequisite   : Python 3.11+, pytest
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
import pytest
from unittest.mock import patch, MagicMock

from src.alerts.ses_client import send_daily_summary, send_trade_alert


class TestSESClient:
    """Tests for SES email client."""
    
    @pytest.fixture
    def mock_settings(self, monkeypatch):
        monkeypatch.setattr("src.alerts.ses_client.settings.ses_sender_email", "test@example.com")
        monkeypatch.setattr("src.alerts.ses_client.settings.aws_region", "us-east-1")
    
    def test_send_daily_summary(self, mock_settings):
        """Test daily summary email."""
        results = [
            {"agent": "buffett", "status": "success", "trades": 2, "value_change": 500},
            {"agent": "bogle", "status": "success", "trades": 0, "value_change": 100},
        ]
        
        with patch("boto3.client") as mock_boto:
            mock_ses = MagicMock()
            mock_ses.send_email.return_value = {"MessageId": "test123"}
            mock_boto.return_value = mock_ses
            
            result = send_daily_summary("user@example.com", results)
            
            assert result is True
            mock_ses.send_email.assert_called_once()
    
    def test_send_trade_alert(self, mock_settings):
        """Test trade alert email."""
        with patch("boto3.client") as mock_boto:
            mock_ses = MagicMock()
            mock_ses.send_email.return_value = {"MessageId": "test456"}
            mock_boto.return_value = mock_ses
            
            result = send_trade_alert(
                recipient="user@example.com",
                agent_name="Warren Buffett",
                trade_type="buy",
                symbol="AAPL",
                shares=100,
                price=175.50,
                reasoning="Strong moat and undervalued",
            )
            
            assert result is True
    
    def test_no_sender_configured(self, monkeypatch):
        """Test graceful handling when sender not configured."""
        monkeypatch.setattr("src.alerts.ses_client.settings.ses_sender_email", "")
        
        result = send_daily_summary("user@example.com", [])
        
        assert result is False
```

**Verification**:
```bash
cd backend
source .venv/bin/activate
pytest tests/test_ses_client.py -v
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Email templates render correctly
- [ ] SES client handles errors gracefully

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/4-1-alerts

---

### Task 4.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] All tests pass
- [ ] Squash merge: `git checkout main && git merge --squash feature/4-1-alerts`
- [ ] Delete branch: `git branch -d feature/4-1-alerts`

---

## Phase 5: Frontend Dashboard

### Task 5.1: React Setup

**Subtask 5.1.1: Vite Project Scaffolding (Single Session)**

**Prerequisites**:
- [x] 4.1.1: Email Client and Templates

**Deliverables**:
- [ ] `frontend/` directory with Vite React project
- [ ] Tailwind CSS configured
- [ ] Basic routing setup
- [ ] API client stub

**Files to Create**:
- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/tailwind.config.js`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/api/client.js`
- `frontend/index.html`

**Complete Code**:

Create `frontend/package.json`:
```json
{
  "name": "council-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "recharts": "^2.10.0",
    "amazon-cognito-identity-js": "^6.3.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.8"
  }
}
```

Create `frontend/vite.config.js`:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
  },
})
```

Create `frontend/tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a365d',
        secondary: '#2d3748',
      },
    },
  },
  plugins: [],
}
```

Create `frontend/postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

Create `frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Council - Legendary Investor AI Agents</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

Create `frontend/src/main.jsx`:
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

Create `frontend/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-gray-50 text-gray-900;
}
```

Create `frontend/src/App.jsx`:
```jsx
import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import AgentDetail from './pages/AgentDetail'
import Login from './pages/Login'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents/:agentId" element={<AgentDetail />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </div>
  )
}

export default App
```

Create `frontend/src/api/client.js`:
```javascript
/**
 * API client for Council backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001'

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('council_token')
  }

  setToken(token) {
    this.token = token
    localStorage.setItem('council_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('council_token')
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken()
        window.location.href = '/login'
      }
      throw new Error(`API error: ${response.status}`)
    }

    return response.json()
  }

  async getDashboard() {
    return this.request('/dashboard')
  }

  async getAgent(agentId) {
    return this.request(`/agents/${agentId}`)
  }

  async getPortfolios() {
    return this.request('/portfolios')
  }

  async getPortfolio(portfolioId) {
    return this.request(`/portfolios/${portfolioId}`)
  }
}

export const apiClient = new ApiClient()
export default apiClient
```

Create `frontend/src/pages/Dashboard.jsx`:
```jsx
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'

const AGENT_COLORS = {
  buffett: 'bg-blue-500',
  graham: 'bg-green-500',
  lynch: 'bg-purple-500',
  dalio: 'bg-orange-500',
  bogle: 'bg-gray-500',
  wood: 'bg-pink-500',
}

function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await apiClient.getDashboard()
        setData(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-primary">Council</h1>
        <p className="text-gray-600">Legendary Investor AI Agents</p>
      </header>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-2">Total Portfolio Value</h2>
        <p className="text-4xl font-bold text-primary">
          ${data?.total_value?.toLocaleString() || '0'}
        </p>
      </div>

      <h2 className="text-2xl font-semibold mb-4">Your Agents</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.agents?.map((agent) => (
          <Link
            key={agent.agent_type}
            to={`/agents/${agent.agent_type}`}
            className="block"
          >
            <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
              <div className="flex items-center mb-4">
                <div className={`w-12 h-12 rounded-full ${AGENT_COLORS[agent.agent_type]} flex items-center justify-center text-white font-bold text-lg`}>
                  {agent.agent_name?.charAt(0) || '?'}
                </div>
                <div className="ml-4">
                  <h3 className="font-semibold text-lg">{agent.agent_name}</h3>
                  <p className="text-gray-500 text-sm capitalize">{agent.agent_type}</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Portfolio Value</span>
                  <span className="font-semibold">${agent.portfolio_value?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Positions</span>
                  <span className="font-semibold">{agent.num_positions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Run</span>
                  <span className="text-sm text-gray-500">
                    {agent.last_run ? new Date(agent.last_run).toLocaleDateString() : 'Never'}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Dashboard
```

Create `frontend/src/pages/AgentDetail.jsx`:
```jsx
import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import apiClient from '../api/client'

function AgentDetail() {
  const { agentId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await apiClient.getAgent(agentId)
        setData(result)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [agentId])

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  const chartData = data?.recent_runs?.map(run => ({
    date: new Date(run.date).toLocaleDateString(),
    value: run.value_after,
  })).reverse() || []

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/" className="text-primary hover:underline mb-4 inline-block">
        Back to Dashboard
      </Link>

      <header className="mb-8">
        <h1 className="text-3xl font-bold text-primary">{data?.agent_name}</h1>
        <p className="text-gray-600 capitalize">{data?.agent_type} Strategy</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm">Total Value</h3>
          <p className="text-2xl font-bold">${data?.portfolio?.total_value?.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm">Cash</h3>
          <p className="text-2xl font-bold">${data?.portfolio?.cash?.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm">Positions</h3>
          <p className="text-2xl font-bold">{data?.portfolio?.positions?.length || 0}</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Portfolio History</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#1a365d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Current Positions</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Symbol</th>
                <th className="text-right py-2">Shares</th>
                <th className="text-right py-2">Avg Cost</th>
                <th className="text-right py-2">Current</th>
                <th className="text-right py-2">Value</th>
                <th className="text-right py-2">Gain/Loss</th>
              </tr>
            </thead>
            <tbody>
              {data?.portfolio?.positions?.map((pos) => (
                <tr key={pos.symbol} className="border-b">
                  <td className="py-2 font-semibold">{pos.symbol}</td>
                  <td className="text-right py-2">{pos.shares}</td>
                  <td className="text-right py-2">${pos.avg_cost?.toFixed(2)}</td>
                  <td className="text-right py-2">${pos.current_price?.toFixed(2)}</td>
                  <td className="text-right py-2">${pos.market_value?.toLocaleString()}</td>
                  <td className={`text-right py-2 ${pos.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {pos.gain_loss_pct?.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
        <div className="space-y-3">
          {data?.recent_transactions?.map((txn) => (
            <div key={txn.transaction_id} className="flex items-center justify-between border-b pb-3">
              <div>
                <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                  txn.type === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {txn.type.toUpperCase()}
                </span>
                <span className="ml-2 font-semibold">{txn.symbol}</span>
                <span className="ml-2 text-gray-600">{txn.shares} shares @ ${txn.price}</span>
              </div>
              <div className="text-gray-500 text-sm">
                {new Date(txn.date).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AgentDetail
```

Create `frontend/src/pages/Login.jsx`:
```jsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    
    // TODO: Implement Cognito authentication
    // For now, just redirect to dashboard
    navigate('/')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
        <h1 className="text-2xl font-bold text-center text-primary mb-6">
          Council Login
        </h1>
        
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>
          
          <button
            type="submit"
            className="w-full bg-primary text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
```

**Verification**:
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

**Success Criteria**:
- [ ] Vite dev server runs
- [ ] Tailwind styles apply
- [ ] Routes work

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/5-1-frontend-setup

---

### Task 5.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] Frontend builds without errors
- [ ] Squash merge: `git checkout main && git merge --squash feature/5-1-frontend-setup`
- [ ] Delete branch: `git branch -d feature/5-1-frontend-setup`

---

## Phase 6: Deployment

### Task 6.1: SAM Deploy

**Subtask 6.1.1: Deploy Backend to AWS (Single Session)**

**Prerequisites**:
- [x] 5.1.1: Vite Project Scaffolding

**Deliverables**:
- [ ] SAM build completes
- [ ] SAM deploy to AWS
- [ ] API Gateway URL working
- [ ] DynamoDB table created

**Commands**:

```bash
cd backend

# Build
sam build --use-container

# Deploy (first time - guided)
sam deploy --guided

# Or deploy with existing config
sam deploy

# Verify deployment
aws cloudformation describe-stacks --stack-name council --query 'Stacks[0].Outputs'
```

**Success Criteria**:
- [ ] CloudFormation stack created
- [ ] Lambda functions deployed
- [ ] API Gateway returns 200
- [ ] DynamoDB table exists

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/6-1-deployment

---

**Subtask 6.1.2: Deploy Frontend to S3/CloudFront (Single Session)**

**Prerequisites**:
- [x] 6.1.1: Deploy Backend to AWS

**Deliverables**:
- [ ] Frontend built for production
- [ ] S3 bucket created
- [ ] Files uploaded to S3
- [ ] CloudFront distribution (optional)

**Commands**:

```bash
cd frontend

# Update API URL
echo "VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/production" > .env.production

# Build
npm run build

# Create S3 bucket
aws s3 mb s3://council-frontend-${RANDOM}

# Upload
aws s3 sync dist/ s3://council-frontend-xxx --delete

# Enable static website hosting
aws s3 website s3://council-frontend-xxx --index-document index.html --error-document index.html

# Set bucket policy for public access
aws s3api put-bucket-policy --bucket council-frontend-xxx --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::council-frontend-xxx/*"
  }]
}'
```

**Success Criteria**:
- [ ] Frontend accessible via S3 URL
- [ ] API calls work from frontend
- [ ] All pages load correctly

**Completion Notes**:
- **Implementation**: (to be filled)
- **Branch**: feature/6-1-deployment

---

### Task 6.1 Complete - Squash Merge

- [ ] All subtasks complete
- [ ] End-to-end flow works
- [ ] Squash merge: `git checkout main && git merge --squash feature/6-1-deployment`
- [ ] Delete branch: `git branch -d feature/6-1-deployment`

---

## Git Workflow Summary

| Phase | Branch | Merge To |
|-------|--------|----------|
| 0 | feature/0-1-project-setup | main |
| 1.1 | feature/1-1-data-fetchers | main |
| 1.2 | feature/1-2-database | main |
| 2.1 | feature/2-1-agents-base | main |
| 2.2 | feature/2-2-agents-value | main |
| 2.3 | feature/2-3-agents-growth | main |
| 3.1 | feature/3-1-api | main |
| 3.2 | feature/3-2-scheduler | main |
| 4.1 | feature/4-1-alerts | main |
| 5.1 | feature/5-1-frontend-setup | main |
| 6.1 | feature/6-1-deployment | main |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| All agents run daily | 100% |
| Test coverage | >80% |
| API response time | <2s |
| Email delivery | <5min |
| Dashboard load time | <2s |
| Multi-user data isolation | 100% |

---

## Post-MVP Backlog

1. **Backtesting Engine** - Test strategies against historical data
2. **Reality Comparison** - Compare agent picks to actual 13F filings
3. **More Agents** - Soros, Icahn, Druckenmiller
4. **Mobile App** - React Native wrapper
5. **Social Features** - Leaderboards, sharing
6. **Webhooks** - Slack/Discord notifications
7. **Performance Analytics** - Sharpe ratio, max drawdown, etc.

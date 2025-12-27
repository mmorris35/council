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

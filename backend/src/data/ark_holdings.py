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

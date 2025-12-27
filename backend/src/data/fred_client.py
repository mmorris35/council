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

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

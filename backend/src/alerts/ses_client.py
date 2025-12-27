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

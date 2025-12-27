# Project Brief: Council

## Overview

| Field | Value |
|-------|-------|
| **Project Name** | Council |
| **Project Type** | web_app |
| **Goal** | AI agents simulating 6 legendary investors make daily decisions, track paper portfolios, and compare against real investor activity |
| **Timeline** | 1 week |
| **Team Size** | 1 |

## Target Users

- Individual investors seeking investment education
- Finance enthusiasts comparing investment philosophies
- Developers interested in AI agent architectures

## Features

### Must-Have (MVP)

1. **6 Investor Agents** - Buffett, Graham, Lynch, Dalio, Bogle, Wood each with distinct logic
2. **Daily Scheduled Runs** - Each agent analyzes markets and makes decisions on schedule
3. **Paper Portfolio Tracking** - Virtual portfolios with buy/sell/hold tracking
4. **Dashboard** - Web UI showing agent wisdom, recommendations, and portfolio state
5. **Reality Comparison** - Compare agent decisions to real investor activity (13F filings, ARK daily)
6. **Historical Performance** - Track portfolio value over time, calculate returns
7. **Email Alerts** - Notify users of significant agent actions
8. **Multi-user Support** - User authentication with isolated data per user

### Nice-to-Have (v2)

- Backtesting against historical data
- User "follow" feature to mirror agent trades
- Push notifications (mobile)
- Additional agents (Soros, Icahn, etc.)
- Social features (compare portfolios)

## Technical Requirements

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Backend Framework | AWS Lambda + API Gateway |
| Database | DynamoDB |
| Scheduler | AWS EventBridge |
| Email | AWS SES |
| Frontend | React + Tailwind (static on S3/CloudFront) |
| IaC | AWS SAM |
| Testing | pytest |
| Data Sources | yfinance, SEC EDGAR, ARK Holdings, FRED |

### Constraints

- Must stay within AWS Free Tier limits
- No Vercel (per user preference)
- Python wherever possible
- Multi-user with data isolation
- Email alerts in MVP (not v2)

### Free Tier Limits (AWS)

| Service | Free Tier |
|---------|-----------|
| Lambda | 1M requests/month, 400k GB-seconds |
| DynamoDB | 25GB storage, 25 RCU/WCU |
| SES | 62k emails/month |
| API Gateway | 1M calls/month |
| S3 | 5GB storage |
| CloudFront | 1TB transfer/month |
| EventBridge | Free for AWS targets |

### Data Source Limits

| Source | Limits | Use Case |
|--------|--------|----------|
| yfinance | Unofficial, no hard limit | Stock prices, fundamentals |
| SEC EDGAR | Free, rate limited | 13F filings (Buffett, etc.) |
| ARK Invest | Free CSVs daily | Cathie Wood holdings |
| FRED | 120 requests/min | Macro data (Dalio) |
| Alpha Vantage | 25/day free | Backup source |

## Agent Specifications

### Warren Buffett Agent
- **Style**: Value investing, buy-and-hold
- **Signals**: P/E < 15, strong moat, consistent earnings
- **Behavior**: Low trade frequency, high conviction
- **Reality Check**: Compare to Berkshire 13F

### Benjamin Graham Agent
- **Style**: Deep value, margin of safety
- **Signals**: P/B < 1.5, current ratio > 2, dividend history
- **Behavior**: Quantitative screening, diversified
- **Reality Check**: Historical Graham criteria backtests

### Peter Lynch Agent
- **Style**: Growth at reasonable price (GARP)
- **Signals**: PEG < 1, revenue growth, category classification
- **Behavior**: Medium frequency, sector diverse
- **Reality Check**: Historical Magellan performance patterns

### Ray Dalio Agent
- **Style**: Risk parity, macro-driven
- **Signals**: Economic indicators, asset correlations
- **Behavior**: Rebalancing, multi-asset
- **Reality Check**: All-Weather portfolio benchmarks

### John Bogle Agent
- **Style**: Passive index, low-cost
- **Signals**: Calendar (monthly buys), age-based allocation
- **Behavior**: Minimal activity, rebalance annually
- **Reality Check**: VOO/BND performance

### Cathie Wood Agent
- **Style**: Disruptive innovation, high growth
- **Signals**: S-curve adoption, patent activity, growth rates
- **Behavior**: High turnover, concentrated positions
- **Reality Check**: ARK daily holdings disclosure

## Success Criteria

1. All 6 agents run daily without errors
2. Paper portfolios update correctly
3. Dashboard loads in < 2 seconds
4. Email alerts deliver within 5 minutes of agent decision
5. Multi-user auth works with data isolation
6. At least 30 days of historical data tracked
7. Reality comparison shows for Buffett (13F) and Wood (ARK)

## Out of Scope

- Real money trading
- Backtesting (v2)
- Mobile app
- Social features
- Payment/subscription system

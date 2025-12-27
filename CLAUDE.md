# Council - Claude Code Rules

## Project Overview

Council is a serverless web application that simulates 6 legendary investors (Buffett, Graham, Lynch, Dalio, Bogle, Wood) as AI agents. Each agent follows its namesake's investment philosophy to manage virtual portfolios, generate daily wisdom, and compare against real investor activity.

## Quick Reference

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Backend | AWS Lambda + API Gateway |
| Database | DynamoDB (single-table design) |
| Auth | AWS Cognito |
| Email | AWS SES |
| Scheduler | AWS EventBridge |
| Frontend | React + Tailwind |
| IaC | AWS SAM |
| Testing | pytest + moto |
| Data Sources | yfinance, SEC EDGAR, ARK, FRED |

## Directory Structure

```
council/
├── backend/
│   ├── src/
│   │   ├── agents/           # 6 investor agents
│   │   │   ├── base.py       # Abstract base class
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
│   │   ├── alerts/           # Email via SES
│   │   ├── api/              # Lambda handlers
│   │   ├── db/               # DynamoDB access
│   │   ├── scheduler/        # Daily run logic
│   │   └── utils/            # Logging, config
│   ├── tests/
│   ├── template.yaml         # SAM template
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── package.json
├── PROJECT_BRIEF.md
├── DEVELOPMENT_PLAN.md
└── CLAUDE.md
```

## Commands

| Command | Purpose |
|---------|---------|
| `cd backend && source .venv/bin/activate` | Activate virtual environment |
| `pip install -r requirements.txt` | Install dependencies |
| `pytest tests/ -v` | Run all tests |
| `pytest tests/ -v --cov=src` | Run tests with coverage |
| `sam validate` | Validate SAM template |
| `sam build --use-container` | Build Lambda functions |
| `sam deploy --guided` | Deploy to AWS |
| `cd frontend && npm run dev` | Start frontend dev server |
| `cd frontend && npm run build` | Build frontend for production |

## Coding Standards

### Python

- Use type hints for all function signatures
- Docstrings for all public functions (Google style)
- Maximum line length: 100 characters
- Use `pydantic` for data validation
- Use `logging` via centralized `get_logger()` - never print()
- No single-letter variable names (except `i`, `j` in loops)
- File headers with author, copyright, license

### File Header Template

```python
"""
Brief description of module.

File Name      : module_name.py
Author         : Mike Morris
Prerequisite   : Python 3.11+
Copyright      : (c) 2024 Mike Morris
License        : GNU GPL
"""
```

### Testing

- Integration tests over heavily mocked unit tests
- Use `moto` for AWS service mocks
- Test real component interactions
- Only mock external services (yfinance, SEC EDGAR)
- Minimum 80% coverage target

### DynamoDB Single-Table Design

Primary Key: `pk` (partition) + `sk` (sort)
GSI1: `gsi1pk` + `gsi1sk`

| Entity | pk | sk | gsi1pk | gsi1sk |
|--------|----|----|--------|--------|
| User | USER#{id} | PROFILE | EMAIL#{email} | USER |
| Portfolio | USER#{id} | PORTFOLIO#{agent} | AGENT#{agent} | USER#{id} |
| Transaction | USER#{id} | TXN#{timestamp}#{id} | AGENT#{agent} | TXN#{timestamp} |
| AgentRun | AGENT#{agent} | RUN#{date} | DATE#{date} | AGENT#{agent} |

### Git Commit Messages

Use semantic commits:
- `feat(scope): description` - New feature
- `fix(scope): description` - Bug fix
- `refactor(scope): description` - Code restructuring
- `test(scope): description` - Adding tests
- `docs(scope): description` - Documentation
- `chore(scope): description` - Maintenance

## Agent Implementation Guidelines

Each agent must:

1. Extend `BaseAgent` class
2. Set `agent_type`, `agent_name`, `description` class attributes
3. Implement `analyze_market()` - return analysis string
4. Implement `generate_recommendations()` - return list of `TradeRecommendation`
5. Follow the investor's actual philosophy closely

### Agent Philosophies Quick Reference

| Agent | Key Metrics | Trading Frequency | Risk Profile |
|-------|-------------|-------------------|--------------|
| Buffett | P/E, moat, margins | Very low | Medium |
| Graham | P/B < 1.5, current ratio > 2 | Low | Low |
| Lynch | PEG < 1, growth | Medium | Medium |
| Dalio | Macro indicators, correlations | Medium | Low |
| Bogle | None (index) | Very low | Matches market |
| Wood | Innovation metrics | High | High |

## Session Checklist

### Starting a Session

- [ ] Read this file (CLAUDE.md)
- [ ] Read DEVELOPMENT_PLAN.md for current status
- [ ] Find next incomplete subtask
- [ ] Create or checkout feature branch
- [ ] Activate virtual environment: `source backend/.venv/bin/activate`

### During Development

- [ ] Follow coding standards above
- [ ] Write tests alongside code
- [ ] Run tests frequently: `pytest tests/ -v`
- [ ] Use logging, not print statements
- [ ] Check types with mypy if available

### Ending a Session

- [ ] All tests pass
- [ ] Run full test suite: `pytest tests/ -v --cov=src`
- [ ] Commit with semantic message
- [ ] Update completion notes in DEVELOPMENT_PLAN.md
- [ ] If task complete, note ready for squash merge

## Environment Variables

Required for local development (create `backend/.env`):

```bash
AWS_REGION=us-east-1
DYNAMODB_TABLE_PREFIX=council-dev
SES_SENDER_EMAIL=noreply@example.com
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Optional - for FRED macro data
FRED_API_KEY=your_key_here

# Optional - backup data source
ALPHA_VANTAGE_KEY=your_key_here
```

## AWS Free Tier Limits

Stay within these limits:

| Service | Limit | Our Usage |
|---------|-------|-----------|
| Lambda | 1M requests/month | ~6 agents x 30 days x users |
| DynamoDB | 25 RCU/WCU | On-demand billing |
| SES | 62k emails/month | Alert emails |
| API Gateway | 1M calls/month | Dashboard requests |
| S3 | 5GB | Frontend static files |
| Cognito | 50k MAU | User auth |

## Troubleshooting

### yfinance rate limiting
If getting blocked, add delays between requests or reduce batch sizes.

### DynamoDB local testing
Use moto for unit tests. For integration tests, consider DynamoDB Local.

### SAM build issues
Use `--use-container` flag to build in Docker for consistent Lambda environment.

## Do Not

- Use Vercel (per user preference)
- Use Conda (ever)
- Comment out existing features to "simplify"
- Use heavily mocked unit tests over integration tests
- Output emoji in scripts
- Use single-letter variable names
- Skip the file header template
- Deploy without testing

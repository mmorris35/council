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

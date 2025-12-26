"""
Configuration module for QRL trading bot.

Centralized configuration management with environment variable support
and validation.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


load_dotenv()


class TradingConfig(BaseModel):
    """Trading configuration with validation."""
    
    symbol: str = Field(default="QRL/USDT", description="Trading pair symbol")
    timeframe: str = Field(default="1d", description="Candlestick timeframe")
    base_order_usdt: float = Field(
        default=50.0,
        gt=0,
        description="Single order size in USDT"
    )
    max_position_usdt: float = Field(
        default=500.0,
        gt=0,
        description="Maximum total position in USDT"
    )
    price_offset: float = Field(
        default=0.98,
        gt=0,
        lt=1,
        description="Limit order price offset (0.98 = 2% below market)"
    )
    
    @field_validator('max_position_usdt')
    @classmethod
    def validate_position_limit(
        cls,
        v: float,
        info
    ) -> float:
        """Ensure max position is greater than single order."""
        if hasattr(info, 'data') and 'base_order_usdt' in info.data:
            if v < info.data['base_order_usdt']:
                raise ValueError(
                    "max_position_usdt must be >= base_order_usdt"
                )
        return v


class ExchangeConfig(BaseModel):
    """Exchange API configuration."""
    
    api_key: Optional[str] = Field(
        default=None,
        description="MEXC API key"
    )
    api_secret: Optional[str] = Field(
        default=None,
        description="MEXC API secret"
    )
    subaccount: Optional[str] = Field(
        default=None,
        description="MEXC subaccount name"
    )
    enable_rate_limit: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )
    
    @classmethod
    def from_env(cls) -> "ExchangeConfig":
        """Load exchange config from environment variables."""
        return cls(
            api_key=os.getenv("MEXC_API_KEY"),
            api_secret=os.getenv("MEXC_API_SECRET"),
            subaccount=os.getenv("MEXC_SUBACCOUNT"),
        )


class MonitoringConfig(BaseModel):
    """Monitoring and alerting configuration."""
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(
        default="logs/trading.log",
        description="Log file path"
    )
    telegram_bot_token: Optional[str] = Field(
        default=None,
        description="Telegram bot token for alerts"
    )
    telegram_chat_id: Optional[str] = Field(
        default=None,
        description="Telegram chat ID for alerts"
    )
    
    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Load monitoring config from environment variables."""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/trading.log"),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )


class AppConfig(BaseModel):
    """Complete application configuration."""
    
    trading: TradingConfig = Field(default_factory=TradingConfig)
    exchange: ExchangeConfig = Field(default_factory=ExchangeConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load complete configuration from environment and defaults."""
        return cls(
            trading=TradingConfig(
                symbol=os.getenv("SYMBOL", "QRL/USDT"),
                base_order_usdt=float(
                    os.getenv("BASE_ORDER_USDT", "50.0")
                ),
                max_position_usdt=float(
                    os.getenv("MAX_POSITION_USDT", "500.0")
                ),
                price_offset=float(os.getenv("PRICE_OFFSET", "0.98")),
            ),
            exchange=ExchangeConfig.from_env(),
            monitoring=MonitoringConfig.from_env(),
        )


# Global configuration instance
config = AppConfig.load()

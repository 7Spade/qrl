"""
Exchange integration module for MEXC cryptocurrency exchange.

This module provides a configured CCXT exchange instance with
API credentials loaded from environment variables.
"""
import os
from typing import Dict, Any, Optional
import ccxt


def get_exchange() -> ccxt.Exchange:
    """
    Create and return a configured MEXC exchange instance.

    Returns:
        ccxt.Exchange: Configured MEXC exchange with API credentials

    Environment Variables:
        MEXC_API_KEY: API key for MEXC exchange
        MEXC_API_SECRET: API secret for MEXC exchange
        MEXC_SUBACCOUNT: (Optional) Subaccount name for subaccount trading
    """
    config: Dict[str, Any] = {
        "apiKey": os.getenv("MEXC_API_KEY"),
        "secret": os.getenv("MEXC_API_SECRET"),
        "enableRateLimit": True,
    }

    subaccount: Optional[str] = os.getenv("MEXC_SUBACCOUNT")
    if subaccount:
        config["options"] = {
            "broker": subaccount,
        }

    exchange: ccxt.Exchange = ccxt.mexc(config)
    return exchange

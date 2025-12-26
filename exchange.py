"""
Exchange integration module for MEXC cryptocurrency exchange.

This module provides a configured CCXT exchange instance with
API credentials loaded from environment variables.
"""
import ccxt
import os

def get_exchange():
    """
    Create and return a configured MEXC exchange instance.
    
    Returns:
        ccxt.Exchange: Configured MEXC exchange with API credentials
        
    Environment Variables:
        MEXC_API_KEY: API key for MEXC exchange
        MEXC_API_SECRET: API secret for MEXC exchange
    """
    exchange = ccxt.mexc({
        "apiKey": os.getenv("MEXC_API_KEY"),
        "secret": os.getenv("MEXC_API_SECRET"),
        "enableRateLimit": True,
    })
    return exchange

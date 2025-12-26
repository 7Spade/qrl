"""
Utility functions for QRL trading bot.

This module provides helper functions for common operations
across the trading bot application.
"""
from datetime import datetime
from typing import Dict, Any


def format_price(price: float, decimals: int = 6) -> str:
    """
    Format price with specified decimal places.
    
    Args:
        price: Price value to format
        decimals: Number of decimal places (default: 6)
        
    Returns:
        str: Formatted price string
    """
    return f"{price:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage value with + or - sign.
    
    Args:
        value: Percentage value to format
        decimals: Number of decimal places (default: 2)
        
    Returns:
        str: Formatted percentage string
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def get_timestamp(utc: bool = True) -> str:
    """
    Get current timestamp string.
    
    Args:
        utc: Use UTC time if True, local time if False
        
    Returns:
        str: Formatted timestamp
    """
    if utc:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.
    
    Args:
        numerator: Top number
        denominator: Bottom number
        default: Value to return if denominator is zero
        
    Returns:
        float: Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_position_usage(current: float, maximum: float) -> float:
    """
    Calculate position usage percentage.
    
    Args:
        current: Current position value
        maximum: Maximum allowed position
        
    Returns:
        float: Position usage percentage (0-100)
    """
    return safe_divide(current, maximum, 0.0) * 100

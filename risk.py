"""
Risk management module for position size control.

This module implements simple risk checks to ensure the trading bot
does not exceed predefined position limits.
"""

def can_buy(current_position_usdt: float, max_position: float) -> bool:
    """
    Check if a new buy order is allowed based on position limits.
    
    Args:
        current_position_usdt: Current position value in USDT
        max_position: Maximum allowed position value in USDT
        
    Returns:
        bool: True if buying is allowed, False if position limit reached
    """
    return current_position_usdt < max_position

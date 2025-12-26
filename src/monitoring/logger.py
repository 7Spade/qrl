"""
Structured logging system for trading bot.

Provides consistent, structured logging across all modules
with proper formatting and log levels.
"""
import os
import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path


class StructuredLogger:
    """
    Structured logger with JSON output support.
    
    Provides consistent logging format across the application
    with structured metadata support.
    """
    
    def __init__(
        self,
        name: str,
        log_file: str = "logs/trading.log",
        log_level: str = "INFO"
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically module name)
            log_file: Log file path
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create logs directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler with structured format
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(levelname)s: %(message)s'
            )
        )
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _format_message(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format message with optional metadata."""
        if metadata:
            return f"{message} | {json.dumps(metadata, default=str)}"
        return message
    
    def info(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info level message."""
        self.logger.info(self._format_message(message, metadata))
    
    def warning(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning level message."""
        self.logger.warning(self._format_message(message, metadata))
    
    def error(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error level message."""
        self.logger.error(self._format_message(message, metadata))
    
    def debug(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug level message."""
        self.logger.debug(self._format_message(message, metadata))
    
    def trade(
        self,
        action: str,
        symbol: str,
        price: float,
        amount: float,
        cost: float
    ) -> None:
        """
        Log trade execution.
        
        Args:
            action: Trade action (BUY/SELL)
            symbol: Trading pair
            price: Execution price
            amount: Amount traded
            cost: Total cost
        """
        self.info(
            f"Trade executed: {action} {symbol}",
            {
                "action": action,
                "symbol": symbol,
                "price": price,
                "amount": amount,
                "cost": cost,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    
    def strategy_signal(
        self,
        strategy: str,
        signal: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log strategy signal generation.
        
        Args:
            strategy: Strategy name
            signal: Signal type (BUY/SELL/HOLD)
            metadata: Additional signal metadata
        """
        self.info(
            f"Strategy signal: {strategy} -> {signal}",
            metadata
        )
    
    def risk_check(
        self,
        passed: bool,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log risk check result.
        
        Args:
            passed: Whether risk check passed
            reason: Check result reason
            metadata: Additional check metadata
        """
        level = "info" if passed else "warning"
        getattr(self, level)(
            f"Risk check: {'PASSED' if passed else 'FAILED'} - {reason}",
            metadata
        )


def get_logger(
    name: str,
    log_file: str = "logs/trading.log",
    log_level: str = "INFO"
) -> StructuredLogger:
    """
    Get or create a structured logger instance.
    
    Args:
        name: Logger name
        log_file: Log file path
        log_level: Logging level
    
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, log_file, log_level)

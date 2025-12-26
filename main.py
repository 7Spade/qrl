"""
Main execution script for QRL trading bot.

Modular architecture with proper separation of concerns
and comprehensive error handling.

Usage:
    python main.py
"""
import sys
from src.core.engine import TradingEngine


def main() -> None:
    """Execute the main trading logic."""
    try:
        engine = TradingEngine()
        engine.execute_trading_cycle()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

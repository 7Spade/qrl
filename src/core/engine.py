"""
Trading engine - Main orchestrator.

Coordinates all modules (strategy, risk, execution, data)
to execute the complete trading cycle.
"""

from typing import Optional
import sys
from src.core.config import AppConfig
from src.data.exchange import ExchangeClient
from src.data.state import StateManager
from src.strategies.base import BaseStrategy
from src.strategies.ema_strategy import EMAAccumulationStrategy
from src.risk.manager import RiskManager
from src.execution.order_manager import OrderManager
from src.monitoring.logger import get_logger


class TradingEngine:
    """
    Main trading engine orchestrating all components.

    Manages the complete trading lifecycle including data fetching,
    strategy analysis, risk checks, and order execution.
    """

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        strategy: Optional[BaseStrategy] = None,
    ):
        """
        Initialize trading engine.

        Args:
            config: Application configuration (loads from env if None)
            strategy: Trading strategy (uses EMA if None)
        """
        self.config = config or AppConfig.load()

        # Initialize logger
        self.logger = get_logger(
            "TradingEngine",
            self.config.monitoring.log_file,
            self.config.monitoring.log_level,
        )

        # Initialize components
        self.exchange = ExchangeClient(
            self.config.exchange, cache_config=self.config.cache
        )
        self.state = StateManager()
        self.risk = RiskManager(
            max_position_usdt=self.config.trading.max_position_usdt,
            max_order_usdt=self.config.trading.base_order_usdt,
        )
        self.order_manager = OrderManager(self.exchange)

        # Initialize strategy
        self.strategy = strategy or EMAAccumulationStrategy()

        self.logger.info(
            "Trading engine initialized",
            {
                "strategy": self.strategy.name,
                "symbol": self.config.trading.symbol,
                "max_position": self.config.trading.max_position_usdt,
            },
        )

    def execute_trading_cycle(self) -> None:
        """
        Execute complete trading cycle.

        Steps:
        1. Fetch market data
        2. Analyze with strategy
        3. Check risk limits
        4. Place order if conditions met
        5. Update state
        """
        try:
            self.logger.info("Starting trading cycle")

            # Step 1: Fetch market data
            ohlcv = self.exchange.fetch_ohlcv(
                self.config.trading.symbol,
                self.config.trading.timeframe,
                limit=120,
            )
            self.logger.debug("Market data fetched", {"candles": len(ohlcv)})

            # Step 2: Strategy analysis
            signal = self.strategy.analyze(ohlcv)
            self.logger.strategy_signal(
                self.strategy.name,
                "BUY" if signal.should_buy else "HOLD",
                signal.metadata,
            )

            if not signal.should_buy:
                self.logger.info("No buy signal - exiting")
                sys.exit(0)

            # Step 3: Risk check
            current_position = self.state.get_position()
            risk_check = self.risk.can_place_order(
                current_position, self.config.trading.base_order_usdt
            )

            self.logger.risk_check(
                risk_check.passed, risk_check.reason, risk_check.metadata
            )

            if not risk_check.passed:
                self.logger.warning("Risk check failed - exiting")
                sys.exit(0)

            # Step 4: Place order
            ticker = self.exchange.fetch_ticker(self.config.trading.symbol)

            order_params = self.order_manager.calculate_order_params(
                ticker["last"],
                self.config.trading.base_order_usdt,
                self.config.trading.price_offset,
            )

            result = self.order_manager.place_limit_buy(
                self.config.trading.symbol,
                order_params["amount"],
                order_params["price"],
            )

            if not result.success:
                self.logger.error(f"Order failed: {result.error}")
                sys.exit(1)

            # Step 5: Update state
            new_position = (
                current_position + self.config.trading.base_order_usdt
            )
            self.state.update_position(new_position)

            self.state.add_trade(
                action="BUY",
                symbol=self.config.trading.symbol,
                price=result.price,
                amount=result.amount,
                cost=result.cost,
                strategy=self.strategy.name,
            )

            self.logger.trade(
                "BUY",
                self.config.trading.symbol,
                result.price,
                result.amount,
                result.cost,
            )

            self.logger.info(
                f"✅ Order completed @ {result.price:.6f}",
                {
                    "position": new_position,
                    "utilization": self.risk.get_position_utilization(
                        new_position
                    ),
                },
            )

        except Exception as e:
            self.logger.error(f"Trading cycle failed: {str(e)}")
            raise

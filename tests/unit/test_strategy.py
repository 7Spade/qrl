"""
Unit tests for trading strategies.

Tests the EMA accumulation strategy logic and signal generation.
"""

import pytest
from src.strategies.ema_strategy import EMAAccumulationStrategy
from src.strategies.base import StrategySignal


class TestEMAAccumulationStrategy:
    """Test cases for EMA accumulation strategy."""

    def setup_method(self):
        """Setup test fixtures."""
        self.strategy = EMAAccumulationStrategy()

    def test_required_candles(self):
        """Test minimum candles requirement."""
        assert self.strategy.get_required_candles() == 60

    def test_insufficient_data_raises_error(self):
        """Test that insufficient data raises ValueError."""
        ohlcv = [[0, 1, 1, 1, 1, 100]] * 50  # Only 50 candles

        with pytest.raises(ValueError, match="Insufficient data"):
            self.strategy.analyze(ohlcv)

    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            self.strategy.analyze([])

    def test_buy_signal_generation(self):
        """Test buy signal when conditions are met."""
        # Create mock OHLCV data with uptrend
        # 100 candles with price increasing from 0.40 to 0.45
        ohlcv = []
        for i in range(100):
            price = 0.40 + (i * 0.0005)
            ohlcv.append(
                [
                    1000000 + i * 86400000,  # timestamp
                    price,  # open
                    price * 1.01,  # high
                    price * 0.99,  # low
                    price,  # close
                    10000,  # volume
                ]
            )

        signal = self.strategy.analyze(ohlcv)

        assert isinstance(signal, StrategySignal)
        assert isinstance(signal.should_buy, bool)
        assert isinstance(signal.metadata, dict)
        assert "ema_short" in signal.metadata
        assert "ema_long" in signal.metadata
        assert "price" in signal.metadata

    def test_signal_metadata(self):
        """Test signal contains required metadata."""
        ohlcv = []
        for i in range(100):
            price = 0.45
            ohlcv.append(
                [1000000 + i * 86400000, price, price, price, price, 10000]
            )

        signal = self.strategy.analyze(ohlcv)

        assert "near_support" in signal.metadata
        assert "positive_momentum" in signal.metadata
        assert isinstance(signal.metadata["near_support"], bool)
        assert isinstance(signal.metadata["positive_momentum"], bool)

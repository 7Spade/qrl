"""
State management module for position tracking and historical data persistence.

Handles persistence of trading position state and OHLCV historical data using SQLite
with proper transaction management and error handling.

Data Lifecycle Strategy:
- Redis: Short-term cache (hours/days) for API call reduction
- SQLite: Long-term persistence (years) for historical analysis
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import (
    create_engine,
    text,
    Engine,
    Column,
    Float,
    String,
    DateTime,
    Integer,
    BigInteger,
    Index,
)
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError


Base = declarative_base()


class Position(Base):
    """Position state model."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    position_usdt = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Trade(Base):
    """Trade history model."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String(10), nullable=False)  # BUY/SELL
    symbol = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    strategy = Column(String(50), nullable=True)


class OHLCVCandle(Base):
    """
    OHLCV candle data for long-term historical storage.

    This table stores historical price data permanently for backtesting
    and technical analysis. Unlike Redis cache (short-term), this data
    is kept indefinitely.

    Storage estimation:
    - 1-minute candles: ~64 bytes per candle
    - 1 day = 1440 candles = ~90 KB
    - 1 year = ~33 MB
    - 10 years = ~330 MB

    With proper indexing, SQLite can efficiently query years of data.
    """

    __tablename__ = "ohlcv_candles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(
        String(10), nullable=False, index=True
    )  # 1m, 5m, 15m, 1h, 4h, 1d
    timestamp = Column(
        BigInteger, nullable=False, index=True
    )  # Unix timestamp in milliseconds
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        # Unique constraint: one candle per symbol/timeframe/timestamp
        Index(
            "idx_symbol_timeframe_timestamp",
            "symbol",
            "timeframe",
            "timestamp",
            unique=True,
        ),
    )


class StateManager:
    """Manages position and trade history state."""

    def __init__(self, db_path: str = "data/state.db"):
        """
        Initialize state manager.

        Args:
            db_path: Path to SQLite database file
        """
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine: Engine = create_engine(f"sqlite:///{db_path}")
        self._init_db()

    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def get_position(self) -> float:
        """
        Get current position value in USDT.

        Returns:
            Current position value, or 0.0 if no position
        """
        try:
            with Session(self.engine) as session:
                position = session.query(Position).first()
                return position.position_usdt if position else 0.0
        except SQLAlchemyError as e:
            print(f"❌ Database read error: {e}")
            return 0.0

    def update_position(self, value: float) -> None:
        """
        Update current position value.

        Args:
            value: New position value in USDT

        Raises:
            ValueError: If value is negative
        """
        if value < 0:
            raise ValueError("Position value cannot be negative")

        try:
            with Session(self.engine) as session:
                position = session.query(Position).first()
                if position:
                    position.position_usdt = value
                    position.updated_at = datetime.utcnow()
                else:
                    position = Position(
                        position_usdt=value, updated_at=datetime.utcnow()
                    )
                    session.add(position)
                session.commit()
        except SQLAlchemyError as e:
            print(f"❌ Database update error: {e}")
            raise

    def add_trade(
        self,
        action: str,
        symbol: str,
        price: float,
        amount: float,
        cost: float,
        strategy: Optional[str] = None,
    ) -> None:
        """
        Record a trade in history.

        Args:
            action: Trade action (BUY/SELL)
            symbol: Trading pair symbol
            price: Execution price
            amount: Amount traded
            cost: Total cost in USDT
            strategy: Strategy name (optional)
        """
        try:
            with Session(self.engine) as session:
                trade = Trade(
                    timestamp=datetime.utcnow(),
                    action=action,
                    symbol=symbol,
                    price=price,
                    amount=amount,
                    cost=cost,
                    strategy=strategy,
                )
                session.add(trade)
                session.commit()
        except SQLAlchemyError as e:
            print(f"❌ Failed to record trade: {e}")
            raise

    def get_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent trade history.

        Args:
            limit: Maximum number of trades to return

        Returns:
            List of trade dictionaries
        """
        try:
            with Session(self.engine) as session:
                trades = (
                    session.query(Trade)
                    .order_by(Trade.timestamp.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "id": t.id,
                        "timestamp": t.timestamp.isoformat(),
                        "action": t.action,
                        "symbol": t.symbol,
                        "price": t.price,
                        "amount": t.amount,
                        "cost": t.cost,
                        "strategy": t.strategy,
                    }
                    for t in trades
                ]
        except SQLAlchemyError as e:
            print(f"❌ Failed to fetch trade history: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate trading statistics.

        Returns:
            Dictionary with statistics (total trades, avg price, etc.)
        """
        try:
            with Session(self.engine) as session:
                trades = session.query(Trade).filter_by(action="BUY").all()

                if not trades:
                    return {
                        "total_trades": 0,
                        "total_cost": 0.0,
                        "avg_price": 0.0,
                        "total_amount": 0.0,
                    }

                total_cost = sum(t.cost for t in trades)
                total_amount = sum(t.amount for t in trades)
                avg_price = (
                    total_cost / total_amount if total_amount > 0 else 0.0
                )

                return {
                    "total_trades": len(trades),
                    "total_cost": total_cost,
                    "avg_price": avg_price,
                    "total_amount": total_amount,
                }
        except SQLAlchemyError as e:
            print(f"❌ Failed to calculate statistics: {e}")
            return {
                "total_trades": 0,
                "total_cost": 0.0,
                "avg_price": 0.0,
                "total_amount": 0.0,
            }

    def save_ohlcv_candles(
        self, symbol: str, timeframe: str, candles: List[List[Any]]
    ) -> int:
        """
        Save OHLCV candles to database for long-term storage.

        This provides persistent historical data storage independent of Redis cache.
        Candles are stored with conflict resolution (upsert behavior).

        Args:
            symbol: Trading pair symbol (e.g., "QRL/USDT")
            timeframe: Candle timeframe (e.g., "1m", "1h", "1d")
            candles: List of OHLCV candles [timestamp, open, high, low, close, volume]

        Returns:
            Number of candles saved

        Example:
            candles = [
                [1640000000000, 0.45, 0.46, 0.44, 0.45, 10000],
                [1640000060000, 0.45, 0.47, 0.45, 0.46, 12000],
            ]
            state_manager.save_ohlcv_candles("QRL/USDT", "1m", candles)
        """
        if not candles:
            return 0

        saved_count = 0
        try:
            with Session(self.engine) as session:
                for candle in candles:
                    timestamp, open_price, high, low, close, volume = candle[
                        :6
                    ]

                    # Check if candle already exists
                    existing = (
                        session.query(OHLCVCandle)
                        .filter_by(
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=int(timestamp),
                        )
                        .first()
                    )

                    if existing:
                        # Update existing candle (in case of corrections)
                        existing.open = float(open_price)
                        existing.high = float(high)
                        existing.low = float(low)
                        existing.close = float(close)
                        existing.volume = float(volume)
                    else:
                        # Insert new candle
                        new_candle = OHLCVCandle(
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=int(timestamp),
                            open=float(open_price),
                            high=float(high),
                            low=float(low),
                            close=float(close),
                            volume=float(volume),
                        )
                        session.add(new_candle)
                        saved_count += 1

                session.commit()
                return saved_count
        except SQLAlchemyError as e:
            print(f"❌ Failed to save OHLCV candles: {e}")
            return 0

    def get_ohlcv_candles(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000,
    ) -> List[List[Any]]:
        """
        Retrieve OHLCV candles from database.

        This allows querying historical data for backtesting and analysis
        without hitting the exchange API.

        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe
            start_time: Start timestamp in milliseconds (optional)
            end_time: End timestamp in milliseconds (optional)
            limit: Maximum number of candles to return

        Returns:
            List of OHLCV candles in standard format
            [timestamp, open, high, low, close, volume]
        """
        try:
            with Session(self.engine) as session:
                query = session.query(OHLCVCandle).filter_by(
                    symbol=symbol, timeframe=timeframe
                )

                if start_time:
                    query = query.filter(OHLCVCandle.timestamp >= start_time)
                if end_time:
                    query = query.filter(OHLCVCandle.timestamp <= end_time)

                candles = (
                    query.order_by(OHLCVCandle.timestamp.asc())
                    .limit(limit)
                    .all()
                )

                return [
                    [c.timestamp, c.open, c.high, c.low, c.close, c.volume]
                    for c in candles
                ]
        except SQLAlchemyError as e:
            print(f"❌ Failed to retrieve OHLCV candles: {e}")
            return []

    def get_candle_count(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Get statistics about stored candles.

        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe

        Returns:
            Dictionary with count, date range, and storage info
        """
        try:
            with Session(self.engine) as session:
                count = (
                    session.query(OHLCVCandle)
                    .filter_by(symbol=symbol, timeframe=timeframe)
                    .count()
                )

                if count == 0:
                    return {
                        "count": 0,
                        "first_timestamp": None,
                        "last_timestamp": None,
                        "storage_mb": 0.0,
                    }

                first_candle = (
                    session.query(OHLCVCandle)
                    .filter_by(symbol=symbol, timeframe=timeframe)
                    .order_by(OHLCVCandle.timestamp.asc())
                    .first()
                )

                last_candle = (
                    session.query(OHLCVCandle)
                    .filter_by(symbol=symbol, timeframe=timeframe)
                    .order_by(OHLCVCandle.timestamp.desc())
                    .first()
                )

                # Estimate storage (approximate 64 bytes per candle)
                storage_mb = (count * 64) / (1024 * 1024)

                return {
                    "count": count,
                    "first_timestamp": (
                        first_candle.timestamp if first_candle else None
                    ),
                    "last_timestamp": (
                        last_candle.timestamp if last_candle else None
                    ),
                    "first_date": (
                        datetime.fromtimestamp(
                            first_candle.timestamp / 1000
                        ).isoformat()
                        if first_candle
                        else None
                    ),
                    "last_date": (
                        datetime.fromtimestamp(
                            last_candle.timestamp / 1000
                        ).isoformat()
                        if last_candle
                        else None
                    ),
                    "storage_mb": round(storage_mb, 2),
                    "estimated_years": (
                        round(count / (365 * 24 * 60), 2)
                        if timeframe == "1m"
                        else None
                    ),
                }
        except SQLAlchemyError as e:
            print(f"❌ Failed to get candle statistics: {e}")
            return {"count": 0, "error": str(e)}

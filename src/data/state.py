"""
State management module for position tracking.

Handles persistence of trading position state using SQLite
with proper transaction management and error handling.
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
                        position_usdt=value,
                        updated_at=datetime.utcnow()
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
        strategy: Optional[str] = None
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
    
    def get_trade_history(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
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
                avg_price = total_cost / total_amount if total_amount > 0 else 0.0
                
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

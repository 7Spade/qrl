"""
State management module for position tracking.

This module handles persistence of trading position state using SQLite,
including automatic database initialization and transaction management.
"""
import os
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError


os.makedirs("data", exist_ok=True)

engine: Engine = create_engine("sqlite:///data/state.db")


def get_position_usdt() -> float:
    """
    Retrieve the current position value from the database.

    Creates the state table if it doesn't exist.

    Returns:
        float: Current position value in USDT, or 0 if no position exists

    Raises:
        SQLAlchemyError: When database operation fails
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(
                "CREATE TABLE IF NOT EXISTS state (pos REAL)"
            ))
            conn.commit()

            result = conn.execute(text("SELECT pos FROM state"))
            row = result.fetchone()
            return float(row[0]) if row else 0.0

    except SQLAlchemyError as e:
        print(f"❌ 資料庫讀取錯誤: {e}")
        raise


def update_position_usdt(value: float) -> None:
    """
    Update the current position value in the database.

    Replaces the existing position value with the new value.

    Args:
        value: New position value in USDT

    Raises:
        SQLAlchemyError: When database operation fails
        ValueError: When value is negative
    """
    if value < 0:
        raise ValueError("Position value cannot be negative")

    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM state"))
            conn.execute(
                text("INSERT INTO state (pos) VALUES (:v)"),
                {"v": value}
            )
            conn.commit()

    except SQLAlchemyError as e:
        print(f"❌ 資料庫更新錯誤: {e}")
        raise

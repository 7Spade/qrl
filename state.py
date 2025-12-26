"""
State management module for position tracking.

This module handles persistence of trading position state using SQLite,
including automatic database initialization and transaction management.
"""
from sqlalchemy import create_engine, text
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///data/state.db")

def get_position_usdt():
    """
    Retrieve the current position value from the database.
    
    Creates the state table if it doesn't exist.
    
    Returns:
        float: Current position value in USDT, or 0 if no position exists
    """
    with engine.connect() as conn:
        result = conn.execute(text(
            "CREATE TABLE IF NOT EXISTS state (pos REAL)"
        ))
        result = conn.execute(text("SELECT pos FROM state"))
        row = result.fetchone()
        return row[0] if row else 0

def update_position_usdt(value: float):
    """
    Update the current position value in the database.
    
    Replaces the existing position value with the new value.
    
    Args:
        value: New position value in USDT
    """
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM state"))
        conn.execute(text("INSERT INTO state (pos) VALUES (:v)"), {"v": value})
        conn.commit()

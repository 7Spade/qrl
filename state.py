from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///data/state.db")

def get_position_usdt():
    with engine.connect() as conn:
        result = conn.execute(text(
            "CREATE TABLE IF NOT EXISTS state (pos REAL)"
        ))
        result = conn.execute(text("SELECT pos FROM state"))
        row = result.fetchone()
        return row[0] if row else 0

def update_position_usdt(value: float):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM state"))
        conn.execute(text("INSERT INTO state (pos) VALUES (:v)"), {"v": value})

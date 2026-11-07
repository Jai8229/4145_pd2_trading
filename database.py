import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "trading_app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 建立持倉與觀察清單資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        shares REAL NOT NULL,
        cost_price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # 建立模擬交易紀錄資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        action TEXT NOT NULL,
        shares REAL NOT NULL,
        price REAL NOT NULL,
        strategy_signal TEXT,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def add_position(ticker: str, shares: float, cost_price: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO portfolio (ticker, shares, cost_price) VALUES (?, ?, ?)",
        (ticker.upper().strip(), shares, cost_price)
    )
    conn.commit()
    conn.close()

def get_portfolio() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, ticker, shares, cost_price, created_at FROM portfolio", conn)
    conn.close()
    return df

def delete_position(position_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolio WHERE id = ?", (position_id,))
    conn.commit()
    conn.close()

def record_trade(ticker: str, action: str, shares: float, price: float, strategy_signal: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trade_history (ticker, action, shares, price, strategy_signal) VALUES (?, ?, ?, ?, ?)",
        (ticker.upper().strip(), action, shares, price, strategy_signal)
    )
    conn.commit()
    conn.close()

def get_trade_history() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, ticker, action, shares, price, strategy_signal, executed_at FROM trade_history ORDER BY executed_at DESC", conn)
    conn.close()
    return df

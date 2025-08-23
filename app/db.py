# app/db.py
import os
import sqlite3
from flask import g

def _connect():
    db_path = os.getenv("DB_PATH", "dmp.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

def get_db():
    """Get a per-request SQLite connection (cached on flask.g)."""
    if "db" not in g:
        g.db = _connect()
    return g.db

def close_db(e=None):
    """Close the connection at the end of the request/app context."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

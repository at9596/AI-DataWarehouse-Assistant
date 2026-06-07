"""
database/connection.py
----------------------
Manages the SQL Server database connection via PyODBC.
Falls back to DEMO_MODE if no real connection is available.
pyodbc is imported lazily so Demo Mode works without libodbc.so.
"""
from __future__ import annotations
from config import DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD, DEMO_MODE


def get_connection():
    """
    Returns a live pyodbc connection to SQL Server.
    Returns None when DEMO_MODE is enabled so the app can run without a DB.
    """
    if DEMO_MODE:
        return None

    try:
        import pyodbc  # lazy import — only needed for live DB
    except ImportError as exc:
        raise RuntimeError(
            "pyodbc / libodbc not installed. Either set DEMO_MODE=true in .env "
            "or install the ODBC Driver: https://learn.microsoft.com/sql/connect/odbc/"
        ) from exc

    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)


def test_connection() -> tuple[bool, str]:
    """
    Tests the database connection and returns (success, message).
    Used in the Streamlit UI to show connection status.
    """
    if DEMO_MODE:
        return True, "✅ Running in Demo Mode (no SQL Server needed)"

    try:
        conn = get_connection()
        conn.close()
        return True, f"✅ Connected to {DB_DATABASE} on {DB_SERVER}"
    except Exception as e:
        return False, f"❌ Connection failed: {e}"

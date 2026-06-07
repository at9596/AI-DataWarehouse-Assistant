"""
config.py
---------
Loads all environment variables from .env and exposes them
as typed constants used throughout the application.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini AI ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── SQL Server ─────────────────────────────────────────────────────────────────
DB_SERVER: str   = os.getenv("DB_SERVER", "localhost")
DB_DATABASE: str = os.getenv("DB_DATABASE", "DataWarehouse")
DB_USERNAME: str = os.getenv("DB_USERNAME", "sa")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

# ── App Mode ──────────────────────────────────────────────────────────────────
# Set DEMO_MODE=true in .env to run the app without a real SQL Server connection.
DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"

# ── Gemini model to use ───────────────────────────────────────────────────────
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

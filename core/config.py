import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment credentials from fyers.env if exists
ENV_PATH = BASE_DIR / "Fyers" / "fyers.env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Database Config
DB_USER = os.getenv("ORACLE_DB_USER", "analysis")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD", "hr")
DB_HOST = os.getenv("ORACLE_DB_HOST", "localhost")
DB_PORT = os.getenv("ORACLE_DB_PORT", "1521")
DB_SERVICE_NAME = os.getenv("ORACLE_DB_SERVICE_NAME", "XE")

# API Server Config
API_TITLE = "Historical Market Intelligence Engine (HMIE) API"
API_VERSION = "1.0.0"
API_PORT = int(os.getenv("PORT", 8000))
API_HOST = os.getenv("HOST", "0.0.0.0")

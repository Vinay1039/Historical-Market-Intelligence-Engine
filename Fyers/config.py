import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from fyers.env if it exists
ENV_PATH = BASE_DIR / "fyers.env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

# FYERS Credentials
FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID", "")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY", "")
FYERS_REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI", "https://myapi.fyers.in/")
FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN", "")

# App Configurations
HISTORY_YEARS = int(os.getenv("HISTORY_YEARS", "15"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))  # Base delay in seconds for backoff

# Directory Paths
OUTPUT_FOLDER = BASE_DIR / "Historical_Data"
LOG_FOLDER = BASE_DIR / "logs"
LOG_FILE = LOG_FOLDER / "Download_Log.txt"
FAILED_SYMBOLS_CSV = BASE_DIR / "failed_symbols.csv"

# Pipeline Settings
FORCE_DOWNLOAD = os.getenv("FORCE_DOWNLOAD", "False").lower() in ("true", "1", "yes")

# Ensure necessary directories exist
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
LOG_FOLDER.mkdir(parents=True, exist_ok=True)

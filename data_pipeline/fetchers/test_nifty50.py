import os
from pathlib import Path
from fyers_apiv3 import fyersModel

# Load credentials from fyers.env in the current directory
ENV_PATH = Path(__file__).resolve().parent / 'fyers.env'
env_vars = {}
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_vars[k.strip()] = v.strip()
            os.environ[k.strip()] = v.strip()

client_id = os.environ.get('FYERS_CLIENT_ID')
access_token = os.environ.get('FYERS_ACCESS_TOKEN')

print(f"Loaded Client ID: {client_id}")
print(f"Loaded Access Token: {access_token[:20]}...{access_token[-10:] if access_token else ''}")

# Initialize Fyers model
fyers = fyersModel.FyersModel(
    client_id=client_id,
    token=access_token,
    is_async=False,
    log_path=""
)

# Test fetching NIFTY50 historical data
# resolution: "D" for Daily, date_format: "1" for yyyy-mm-dd
data = {
    "symbol": "NSE:NIFTY50-INDEX",
    "resolution": "D",
    "date_format": "1",
    "range_from": "2024-01-01",
    "range_to": "2024-01-10",
    "cont_flag": "1"
}

print("\nFetching NIFTY50 data...")
response = fyers.history(data=data)
print("API Response:")
print(response)
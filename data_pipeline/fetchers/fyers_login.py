import os
import json
import webbrowser
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from fyers_apiv3 import fyersModel

ENV_PATH = Path(__file__).resolve().parent / 'fyers.env'
env_vars = {}
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_vars[k.strip()] = v.strip()
            os.environ[k.strip()] = v.strip()

client_id = os.environ.get('FYERS_CLIENT_ID', '')
secret_key = os.environ.get('FYERS_SECRET_KEY', '')
redirect_uri = os.environ.get('FYERS_REDIRECT_URI', 'https://127.0.0.1/')

if not redirect_uri.endswith('/'):
    redirect_uri += '/'

print("=" * 60)
print("FYERS Token Generator (New Directory)")
print("=" * 60)
print(f"Client ID    : {client_id}")
print(f"Redirect URI : {redirect_uri}")
print()

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type="code",
    grant_type="authorization_code"
)

auth_url = session.generate_authcode()

print("Step 1: Opening browser for login...")
print(f"URL: {auth_url}")
print()
webbrowser.open(auth_url)

print("Step 2: After login, copy the redirected URL from your browser address bar.")
callback_url = input("Paste the full redirect URL here: ").strip()

auth_code = None
try:
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    auth_code = params.get('auth_code', [None])[0]
    if not auth_code:
        code_param = params.get('code', [None])[0]
        if code_param and len(code_param) > 50:
            auth_code = code_param
        elif 'auth_code=' in callback_url:
            auth_code = callback_url.split('auth_code=')[1].split('&')[0]
        elif 'code=' in callback_url:
            potential_code = callback_url.split('code=')[1].split('&')[0]
            if len(potential_code) > 50:
                auth_code = potential_code
    if not auth_code:
        print("ERROR: Could not extract auth code from URL.")
        exit(1)
    print(f"\nExtracted auth code: {auth_code[:20]}...{auth_code[-10:]}")
except Exception as e:
    print(f"ERROR parsing URL: {e}")
    exit(1)

print("\nStep 3: Exchanging auth code for access token...")
try:
    session.set_token(auth_code)
    resp_json = session.generate_token()
    print(f"Response: {json.dumps(resp_json, indent=2)}")

    if resp_json.get('s') == 'ok' or 'access_token' in resp_json:
        access_token = resp_json.get('access_token')
        print(f"\n✅ SUCCESS! Access token obtained.")
        
        # Update fyers.env in Fyers directory
        lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
        new_lines = []
        updated = False
        for line in lines:
            if line.startswith('FYERS_ACCESS_TOKEN='):
                new_lines.append(f'FYERS_ACCESS_TOKEN={access_token}')
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f'FYERS_ACCESS_TOKEN={access_token}')
            
        # Ensure client_id, secret_key, redirect_uri are also persisted
        for key, val in [('FYERS_CLIENT_ID', client_id), ('FYERS_SECRET_KEY', secret_key), ('FYERS_REDIRECT_URI', redirect_uri)]:
            if not any(line.startswith(f"{key}=") for line in new_lines):
                new_lines.insert(0, f"{key}={val}")

        ENV_PATH.write_text('\n'.join(new_lines) + '\n')
        print(f"\n✅ fyers.env updated with new access token.")
    else:
        print(f"\n❌ Token exchange failed: {resp_json.get('message', 'Unknown error')}")
except Exception as e:
    print(f"\n❌ Request failed: {e}")
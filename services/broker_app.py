# services/broker_app.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BROKER_API_KEY = os.environ.get("ALPACA_API_KEY")
BROKER_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")

BASE_URL = "https://broker-api.sandbox.alpaca.markets/v1"

HEADERS = {
    "APCA-API-KEY-ID": BROKER_API_KEY,
    "APCA-API-SECRET-KEY": BROKER_SECRET_KEY,
    "Content-Type": "application/json"
}

def list_accounts():
    url = f"{BASE_URL}/accounts"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # raise exception if unauthorized or failed
    return response.json()  # returns a list of account dicts

def get_account(account_id):
    url = f"{BASE_URL}/accounts/{account_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def load_account_snapshot():
    accounts = list_accounts()
    account_id = accounts[0]["id"]
    return get_account(account_id)
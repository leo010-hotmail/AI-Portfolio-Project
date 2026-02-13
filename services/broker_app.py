# services/broker_app.py
import os
import requests
from dotenv import load_dotenv
#from alpaca.broker.client import BrokerClient
#from alpaca.broker.requests import MarketOrderRequest, LimitOrderRequest
#from alpaca.trading.enums import OrderSide, TimeInForce

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

#def load_account_snapshot():
#    accounts = list_accounts()
#    account_id = accounts[0]["id"]
#    return get_account(account_id)

def place_order(account_id, symbol, quantity, side, order_type="market", price=None):
    url = f"{BASE_URL}/trading/accounts/{account_id}/orders"

    order_data = {
        "symbol": symbol,
        "qty": quantity,
        "side": side.lower(),  # "buy" or "sell"
        "type": order_type.lower(),  # "market" or "limit"
        "time_in_force": "day"
    }

    if order_type.lower() == "limit" and price:
        order_data["limit_price"] = str(price)

    response = requests.post(url, json=order_data, headers=HEADERS)
    response.raise_for_status()

    return response.json()

def list_orders(account_id, limit=5):
    url = f"{BASE_URL}/trading/accounts/{account_id}/orders"

    params = {
        "status": "all",      # open, closed, all
        "direction": "desc",  # newest first
        "limit": limit
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def list_positions(account_id):
    url = f"{BASE_URL}/trading/accounts/{account_id}/positions"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_trading_account_details(account_id):
    url = f"{BASE_URL}/trading/accounts/{account_id}/account"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()
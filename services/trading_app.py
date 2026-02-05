# services/trading_app.py
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus

def get_trading_client(account_id: str):
    return TradingClient(
        api_key=os.getenv("ALPACA_API_KEY"),
        secret_key=os.getenv("ALPACA_SECRET_KEY"),
        paper=True,
        account_id=account_id
    )

def get_account_snapshot(account_id: str) -> dict:
    client = get_trading_client(account_id)

    account = client.get_account()
    positions = client.get_all_positions()

    orders_request = GetOrdersRequest(
        status=OrderStatus.OPEN
    )
    orders = client.get_orders(orders_request)

    return {
        "name": account.account_number,
        "equity": account.equity,
        "cash": account.cash,
        "positions": positions,
        "open_orders": orders
    }

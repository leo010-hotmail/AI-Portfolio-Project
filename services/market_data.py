import os
import requests

ALPACA_DATA_URL = "https://data.sandbox.alpaca.markets/v2/stocks/{symbol}/snapshot?feed=delayed_sip"
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")


class AlpacaMarketDataError(Exception):
    pass


def fetch_market_data(symbol: str) -> dict:
    symbol = (symbol or "").strip().upper()
    if not symbol:
        raise AlpacaMarketDataError("Symbol is required to fetch market data.")

    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        raise AlpacaMarketDataError("Alpaca credentials are not configured.")

    url = ALPACA_DATA_URL.format(symbol=symbol)

    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise AlpacaMarketDataError(
            f"Snapshot request failed: {response.status_code} - {response.text}"
        )

    data = response.json()

    if not data:
        raise AlpacaMarketDataError("No data returned from Alpaca snapshot API.")

    latest_trade = data.get("latestTrade", {})
    latest_quote = data.get("latestQuote", {})
    daily_bar = data.get("dailyBar", {})
    prev_daily_bar = data.get("prevDailyBar", {})

    current_price = latest_trade.get("p")
    previous_close = prev_daily_bar.get("c")

    change_pct = None
    if current_price and previous_close:
        change_pct = ((current_price - previous_close) / previous_close) * 100

    return {
        "symbol": symbol,
        "current_price": current_price,
        "open": daily_bar.get("o"),
        "high": daily_bar.get("h"),
        "low": daily_bar.get("l"),
        "previous_close": previous_close,
        "volume": daily_bar.get("v"),
        "change_pct": change_pct,
        "exchange": latest_quote.get("x"),
        "bid": latest_quote.get("bp"),
        "ask": latest_quote.get("ap"),
    }

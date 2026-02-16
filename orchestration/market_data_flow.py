import streamlit as st
from services.market_data import fetch_market_data, fetch_30_day_history, bars_to_dataframe


FIELD_PROMPT = "Which stock symbol would you like market data for?"


def format_price(value):
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_volume(value):
    if value is None:
        return "N/A"
    return f"{int(value):,}"


def format_percentage(value):
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def summarize_market_data(data):
    lines = [
        f"- **Current Price:** {format_price(data.get('current_price'))}",
        f"- **Open:** {format_price(data.get('open'))}",
        f"- **High (Day):** {format_price(data.get('high'))}",
        f"- **Low (Day):** {format_price(data.get('low'))}",
        f"- **Previous Close:** {format_price(data.get('previous_close'))}",
        f"- **Volume:** {format_volume(data.get('volume'))}",
        f"- **Change:** {format_percentage(data.get('change_pct'))}",
        f"- **Bid:** {format_price(data.get('bid'))}",
        f"- **Ask:** {format_price(data.get('ask'))}",
    ]

    return (
        f"### Market Update — {data.get('symbol')}\n"
        + "\n".join(lines)
        + "\n\nLet me know if you want information on another symbol."
    )


def handle_market_data_flow(parsed_params, user_input):
    trade_state = st.session_state.trade_state
    symbol = parsed_params.get("symbol")
    if symbol:
        trade_state["symbol"] = symbol.strip().upper()

    if trade_state.get("expected_field") == "symbol" and user_input:
        trade_state["symbol"] = user_input.strip().upper()
        trade_state.pop("expected_field", None)

    if not trade_state.get("symbol"):
        trade_state["expected_field"] = "symbol"
        return FIELD_PROMPT

    symbol = trade_state["symbol"]

    try:
        data = fetch_market_data(symbol)
        bars = fetch_30_day_history(symbol)
        df = bars_to_dataframe(bars)

        st.session_state.last_chart = df.sort_index()
        st.session_state.last_chart_symbol = symbol
    except Exception as exc:
        trade_state.pop("symbol", None)
        trade_state.pop("expected_field", None)
        return (
            f"Sorry, I couldn't retrieve market data for `{symbol}`. "
            f"{str(exc)}"
        )

    st.session_state.trade_state = {}
    return summarize_market_data(data)

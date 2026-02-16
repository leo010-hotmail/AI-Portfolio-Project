import streamlit as st
from services.trade_api import TradeService


trade_service = TradeService()


def format_price(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_quantity(value):
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return "N/A"


def summarize_order(order):
    order_id = order.get("id", "unknown")
    symbol = order.get("symbol", "N/A")
    side = order.get("side", "N/A").upper()
    qty = format_quantity(order.get("qty") or order.get("filled_qty"))
    order_type = order.get("type", "N/A").upper()
    status = order.get("status", "N/A")
    price = order.get("limit_price") or order.get("price")
    price_section = f" at {format_price(price)}" if price else ""
    submitted_at = order.get("submitted_at") or order.get("created_at")

    lines = [
        f"- **Order ID:** `{order_id}`",
        f"  - **Symbol:** {symbol}",
        f"  - **Side:** {side}",
        f"  - **Quantity:** {qty}",
        f"  - **Type:** {order_type}{price_section}",
        f"  - **Status:** {status}",
    ]

    if submitted_at:
        lines.append(f"  - **Submitted:** {submitted_at}")

    filled_qty = order.get("filled_qty")
    if filled_qty and filled_qty not in (0, "0", "0.0"):
        lines.append(f"  - **Filled:** {format_quantity(filled_qty)}")

    return "\n".join(lines)


def handle_view_orders_flow():
    st.session_state.trade_state = {}

    try:
        orders = trade_service.list_open_orders(limit=100, status="open")
    except Exception as exc:
        return (
            "Sorry, I couldn't retrieve your open orders right now. "
            f"{str(exc)}"
        )

    if not orders:
        return "You don't have any open orders at the moment."

    lines = [
        f"### Open Orders ({len(orders)})",
        "Here are your currently active orders:",
        ""
    ]

    for order in orders:
        lines.append(summarize_order(order))
        lines.append("")  # blank line between orders

    lines.append("Let me know if you want to cancel one of these or place a new trade.")
    return "\n".join(lines).strip()

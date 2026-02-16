import streamlit as st
from services.broker_app import list_accounts, list_positions


def _get_primary_account_id():
    accounts = list_accounts()
    if not accounts:
        raise RuntimeError("No trading accounts could be loaded.")
    return accounts[0]["id"]


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_currency(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def _format_percentage(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if abs(numeric) < 2:
        numeric *= 100

    return f"{numeric:.2f}%"


def _format_quantity(value):
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        if value is None:
            return "0"
        return str(value)


def _summarize_position(position):
    symbol = position.get("symbol", "N/A")
    qty = _format_quantity(position.get("qty"))
    market_value = _format_currency(position.get("market_value"))
    avg_entry = position.get("avg_entry_price") or position.get("avg_price")
    unrealized = position.get("unrealized_pl")
    unrealized_pct = (
        position.get("unrealized_plpc")
        or position.get("unrealized_pl_pct")
        or position.get("unrealized_return_pct")
    )

    lines = [
        f"- **{symbol}**",
        f"  - Quantity: {qty}",
        f"  - Market value: {market_value}",
    ]

    if avg_entry:
        lines.append(f"  - Avg entry: {_format_currency(avg_entry)}")

    if unrealized:
        pl_line = f"  - Unrealized P/L: {_format_currency(unrealized)}"
        if unrealized_pct:
            pl_line += f" ({_format_percentage(unrealized_pct)})"
        lines.append(pl_line)

    return "\n".join(lines)


def handle_view_portfolio_flow():
    st.session_state.trade_state = {}

    try:
        account_id = _get_primary_account_id()
        positions = list_positions(account_id)
    except Exception as exc:
        return (
            "Sorry, I couldn't retrieve your positions right now. "
            f"{str(exc)}"
        )

    if not positions:
        return "You currently have no holdings in this account."

    total_value = sum(_safe_float(pos.get("market_value")) for pos in positions)
    sorted_positions = sorted(
        positions,
        key=lambda p: _safe_float(p.get("market_value")),
        reverse=True
    )

    top_positions = sorted_positions[:5]

    lines = [
        "### Portfolio Snapshot",
        f"- **Total market value:** {_format_currency(total_value)}",
        f"- **Positions:** {len(positions)}",
        "",
        "Top holdings:",
    ]

    for position in top_positions:
        lines.append(_summarize_position(position))
        lines.append("")

    remaining = len(positions) - len(top_positions)
    if remaining > 0:
        lines.append(f"...and {remaining} more positions.")

    lines.append("Let me know if you want details on one of these or need a new trade.")
    return "\n".join(lines).strip()

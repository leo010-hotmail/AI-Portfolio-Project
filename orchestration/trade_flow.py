import streamlit as st
from services.trade_api import TradeService
from services.broker_app import list_accounts, list_orders

trade_service = TradeService()

PLACE_TRADE_FIELDS = ["action", "symbol", "quantity", "order_type", "account"]
CANCEL_TRADE_FIELDS = ["cancel_symbol"]
FLOW_REQUIRED_FIELDS = {
    "place_trade": PLACE_TRADE_FIELDS,
    "cancel_order": CANCEL_TRADE_FIELDS
}

FIELD_PROMPTS = {
    "action": "Do you want to buy or sell?",
    "symbol": "Which stock would you like to trade?",
    "cancel_symbol": "Which stock trade would you like to cancel?",
    "quantity": "How many shares would you like to trade?",
    "order_type": "Is this a market order or a limit order?",
    "price": "What limit price would you like to use?",
    "account": "Which account should I use? (Cash, TFSA, RRSP)",
    "order_id": "Please provide the order ID you want to cancel."
}

AFFIRMATIVE_PREFIXES = ("yes", "y", "sure", "confirm", "yep", "ok", "okay", "go ahead", "please do")
NEGATIVE_PREFIXES = ("no", "nah", "cancel", "stop", "don't", "do not", "not now")


def coerce_value(field, user_input):
    if not isinstance(user_input, str):
        return user_input

    user_input = user_input.strip()

    if field == "quantity":
        return int(user_input)

    if field == "price":
        return float(user_input)

    if field == "action":
        val = user_input.lower()
        if val in ["buy", "purchase"]:
            return "buy"
        if val in ["sell"]:
            return "sell"
        raise ValueError("Action must be buy or sell")

    if field == "symbol":
        return user_input.upper()

    if field == "order_type":
        user_input = user_input.lower()
        if user_input in ["market"]:
            return "market"
        elif user_input in ["limit"]:
            return "limit"
        else:
            raise ValueError("Order type must be market or limit")

    if field == "account":
        return user_input.upper()

    if field == "order_id":
        return user_input

    return user_input


def get_primary_account_id():
    accounts = list_accounts()
    return accounts[0]["id"]


def find_open_orders_by_symbol(symbol):
    account_id = get_primary_account_id()
    orders = list_orders(account_id, limit=100, status="open")
    symbol = symbol.upper()
    return [
        order for order in orders
        if order.get("symbol", "").upper() == symbol
    ]


def get_order_summary(order):
    symbol = order.get("symbol", "N/A")
    side = order.get("side", "N/A")
    qty = order.get("qty", "N/A")
    order_type = order.get("type", "N/A")
    order_id = order.get("id", "N/A")
    status = order.get("status", "N/A")
    price = order.get("limit_price") or order.get("price")

    price_info = f" @ ${price}" if price else ""
    return (
        f"ID `{order_id}` — {side.upper()} {qty} {symbol} {order_type.upper()}{price_info}\n"
        f"    Status: {status}"
    )


def build_cancel_selection_prompt(symbol, orders):
    lines = [f"I found {len(orders)} open orders for `{symbol}`:"]
    for idx, order in enumerate(orders, start=1):
        summary = get_order_summary(order)
        lines.append(f"{idx}. {summary}")
    lines.append("Please reply with the number or exact order ID for the order you want to cancel.")
    return "\n".join(lines)


def clear_cancel_lookup_state(trade_state):
    for field in ["cancel_candidates", "cancel_candidates_symbol", "selection_prompt", "awaiting_selection"]:
        trade_state.pop(field, None)


def find_open_order(order_id):
    account_id = get_primary_account_id()
    orders = list_orders(account_id, limit=50, status="open")
    for order in orders:
        if str(order.get("id")) == str(order_id):
            return order
    return None


def ensure_matching_open_order(trade_state):
    if trade_state.get("matched_order"):
        return trade_state["matched_order"]
    order_id = trade_state.get("order_id")
    if not order_id:
        return None
    match = find_open_order(order_id)
    if match:
        trade_state["matched_order"] = match
    return match


def get_next_missing_field(flow, trade_state):
    if flow == "cancel_order":
        return None

    required_fields = FLOW_REQUIRED_FIELDS.get(flow, [])
    for field in required_fields:
        if field not in trade_state or trade_state[field] is None:
            return field
    if flow == "place_trade" and trade_state.get("order_type") == "limit" and trade_state.get("price") is None:
        return "price"
    return None


def prompt_for_field(field):
    return FIELD_PROMPTS[field]


def looks_like_affirmation(text):
    normalized = text.lower().strip()
    return any(normalized.startswith(prefix) for prefix in AFFIRMATIVE_PREFIXES)


def looks_like_negation(text):
    normalized = text.lower().strip()
    return any(normalized.startswith(prefix) for prefix in NEGATIVE_PREFIXES)


def summarize_trade(trade):
    action = trade["action"].capitalize()
    symbol = trade["symbol"]
    quantity = trade["quantity"]
    order_type = trade["order_type"].capitalize()
    account = trade["account"].upper()

    lines = [
        f"- **Action:** {action}",
        f"- **Symbol:** {symbol}",
        f"- **Quantity:** {quantity}",
        f"- **Order Type:** {order_type}",
        f"- **Account:** {account}",
    ]

    if trade["order_type"] == "limit":
        price = trade["price"]
        total_cost = quantity * price
        lines.append(f"- **Price:** ${price}")
        lines.append(f"- **Estimated Cost:** ${total_cost}")

    return (
        "### Trade Summary\n"
        + "\n".join(lines)
        + "\n\nWould you like me to place this trade?\n(Yes / No)"
    )


def summarize_cancel(trade_state):
    order = trade_state.get("matched_order")

    if not order:
        return "I need to locate the order before I can summarize it."

    order_id = order.get("id", trade_state.get("order_id"))
    symbol = order.get("symbol", "N/A")
    quantity = order.get("qty", "N/A")
    side = order.get("side", "N/A").capitalize()
    order_type = order.get("type", "N/A").capitalize()
    status = order.get("status", "N/A")

    lines = [
        f"- **Order ID:** {order_id}",
        f"- **Symbol:** {symbol}",
        f"- **Quantity:** {quantity}",
        f"- **Side:** {side}",
        f"- **Order Type:** {order_type}",
        f"- **Status:** {status}",
    ]

    limit_price = order.get("limit_price") or order.get("price")
    if limit_price:
        lines.append(f"- **Limit Price:** ${limit_price}")

    return (
        "### Cancel Summary\n"
        + "\n".join(lines)
        + "\n\nWould you like me to cancel this order?\n(Yes / No)"
    )


def summarize_flow(flow, trade_state):
    if flow == "cancel_order":
        message = summarize_cancel(trade_state)
    else:
        message = summarize_trade(trade_state)
    trade_state["awaiting_confirmation"] = True
    return message


def apply_candidate_selection(user_input, trade_state):
    candidates = trade_state.get("cancel_candidates", [])
    if not candidates:
        return False

    normalized = user_input.strip()
    if normalized.isdigit():
        idx = int(normalized) - 1
        if 0 <= idx < len(candidates):
            order = candidates[idx]
            trade_state["order_id"] = order.get("id")
            trade_state["matched_order"] = order
            return True

    normalized_lower = normalized.lower()
    for order in candidates:
        order_id = str(order.get("id", "")).lower()
        if order_id and (normalized_lower == order_id or order_id in normalized_lower):
            trade_state["order_id"] = order.get("id")
            trade_state["matched_order"] = order
            return True

    return False


def prepare_cancel_candidates(trade_state):
    if trade_state.get("order_id"):
        return None

    if trade_state.get("awaiting_selection"):
        return trade_state.get("selection_prompt")

    symbol = trade_state.get("symbol")
    if not symbol:
        clear_cancel_lookup_state(trade_state)
        trade_state["expected_field"] = "symbol"
        return prompt_for_field("cancel_symbol")

    stored_symbol = trade_state.get("cancel_candidates_symbol")
    if stored_symbol == symbol and trade_state.get("cancel_candidates"):
        orders = trade_state["cancel_candidates"]
    else:
        orders = find_open_orders_by_symbol(symbol)
        trade_state["cancel_candidates"] = orders
        trade_state["cancel_candidates_symbol"] = symbol

    if not orders:
        trade_state.pop("symbol", None)
        clear_cancel_lookup_state(trade_state)
        return (
            f"I couldn't find any open orders for `{symbol}`. "
            "Please provide another symbol or the exact order ID."
        )

    if len(orders) == 1:
        order = orders[0]
        trade_state["order_id"] = order.get("id")
        trade_state["matched_order"] = order
        clear_cancel_lookup_state(trade_state)
        return None

    prompt = build_cancel_selection_prompt(symbol, orders)
    trade_state["selection_prompt"] = prompt
    trade_state["awaiting_selection"] = True
    trade_state["expected_field"] = "order_id"
    return prompt


def handle_trade_flow(parsed_params, user_input):
    trade_state = st.session_state.trade_state
    flow = trade_state.get("flow", "place_trade")

    if trade_state.get("awaiting_confirmation"):
        normalized = user_input.lower().strip()
        if looks_like_affirmation(normalized):
            if flow == "cancel_order":
                order_id = trade_state.get("order_id")
                result = trade_service.cancel_trade(order_id)
            else:
                result = trade_service.place_trade(trade_state)
            st.session_state.trade_state = {}
            return result
        if looks_like_negation(normalized):
            st.session_state.trade_state = {}
            return "Okay, I’ve cancelled the request."

    for field, value in parsed_params.items():
        if value is not None:
            trade_state[field] = coerce_value(field, value)

    if flow == "place_trade" and trade_state.get("price") is not None:
        trade_state.setdefault("order_type", "limit")

    if "expected_field" in trade_state and user_input:
        field = trade_state["expected_field"]
        try:
            trade_state[field] = coerce_value(field, user_input)
            trade_state.pop("expected_field", None)
        except ValueError:
            return prompt_for_field(field)

    if flow == "cancel_order" and trade_state.get("awaiting_selection") and user_input:
        if apply_candidate_selection(user_input, trade_state):
            trade_state.pop("awaiting_selection", None)
            trade_state.pop("selection_prompt", None)
            trade_state.pop("expected_field", None)
        else:
            return trade_state.get("selection_prompt")

    if flow == "cancel_order":
        candidate_prompt = prepare_cancel_candidates(trade_state)
        if candidate_prompt:
            return candidate_prompt

    next_field = get_next_missing_field(flow, trade_state)
    if next_field:
        trade_state["expected_field"] = next_field
        return prompt_for_field(next_field)

    if flow == "cancel_order":
        match = ensure_matching_open_order(trade_state)
        if match is None:
            order_id = trade_state.get("order_id")
            trade_state.pop("order_id", None)
            trade_state.pop("matched_order", None)
            trade_state.pop("expected_field", None)
            return (
                f"I couldn't find an open order with ID `{order_id}`. "
                "Please double-check the ID or let me know another order to cancel."
            )

    return summarize_flow(flow, trade_state)

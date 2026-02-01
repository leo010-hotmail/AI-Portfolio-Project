import streamlit as st
from services.trade_api import TradeService

trade_service = TradeService()

REQUIRED_TRADE_FIELDS = ["action","symbol", "quantity", "order_type", "account"]

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

    return user_input

def get_next_missing_field(trade_state):
    for field in REQUIRED_TRADE_FIELDS:
        if field not in trade_state or trade_state[field] is None:
            return field
    # 🔑 price only required for LIMIT orders
    if trade_state.get("order_type") == "limit" and trade_state.get("price") is None:
        return "price"
    return None

def handle_trade_flow(parsed_params, user_input):
    trade_state = st.session_state.trade_state

    # ---------- Confirmation ----------
    if user_input.lower() in ["yes", "confirm", "place trade"]:
        result = trade_service.place_trade(trade_state)
        st.session_state.trade_state = {}
        return result

    if user_input.lower() in ["no", "cancel"]:
        st.session_state.trade_state = {}
        return "Okay, I’ve cancelled the trade."

    # ---------- Fill from LLM extraction ----------
    for field, value in parsed_params.items():
        if value is not None:
            trade_state[field] = coerce_value(field, value)

    # 🔑 If price is present, infer LIMIT order
    if trade_state.get("price") is not None:
        trade_state.setdefault("order_type", "limit")

    # ---------- Handle reply to expected field ----------
    if "expected_field" in trade_state and user_input:
        field = trade_state["expected_field"]
        try:
            trade_state[field] = coerce_value(field, user_input)
            trade_state.pop("expected_field")
        except ValueError:
            return prompt_for_field(field)

    # ---------- Ask ONLY for the next missing field ----------
    next_field = get_next_missing_field(trade_state)
    if next_field:
        trade_state["expected_field"] = next_field
        return prompt_for_field(next_field)

    # ---------- All required fields collected ----------
    return summarize_trade(trade_state)

def prompt_for_field(field):
    prompts = {
        "action": "Do you want to buy or sell?",
        "symbol": "Which stock would you like to trade?",
        "quantity": "How many shares would you like to trade?",
        "order_type": "Is this a market order or a limit order?",
        "price": "What limit price would you like to use?",
        "account": "Which account should I use? (Cash, TFSA, RRSP)"
    }
    return prompts[field]

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

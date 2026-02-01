from llm import get_llm_client
from orchestration.trade_flow import handle_trade_flow
import streamlit as st

llm = get_llm_client()


def handle_user_input(user_input: str):
    # 🔑 Step 1: if a trade is in progress, continue it
    trade_state = st.session_state.get("trade_state", {})

    if trade_state and (
        len(trade_state) > 0 or "expected_field" in trade_state
    ):
        parsed = llm.parse(user_input)
        return handle_trade_flow(parsed, user_input)

    # Step 2: classify intent ONLY if no active trade
    intent_result = llm.classify_intent(user_input)
    intent = intent_result.get("intent")

    # Step 3: start new trade flow
    if intent == "place_trade":
        parsed = llm.parse(user_input)
        return handle_trade_flow(parsed, user_input)

    return "Sorry, I didn’t understand your request."





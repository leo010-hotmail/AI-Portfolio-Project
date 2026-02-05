from llm import get_llm_client
from orchestration.trade_flow import handle_trade_flow
import streamlit as st

MAX_LLM_CALLS = 30
MAX_CHARS = 200

llm = get_llm_client()


def handle_user_input(user_input: str):
    if "llm_calls" not in st.session_state:
        st.session_state.llm_calls = 0

    if st.session_state.llm_calls >= MAX_LLM_CALLS:
        return (
            "⚠️ You've reached the maximum number of AI requests "
            "for this session. Please refresh the app to start over."
        )

    # count this interaction
    st.session_state.llm_calls += 1

    # 🔑 Step 1: if a trade is in progress, continue it
    trade_state = st.session_state.get("trade_state", {})

    if trade_state and (
        len(trade_state) > 0 or "expected_field" in trade_state
    ):
    
        if len(user_input) > MAX_CHARS:
            return "Please keep your message under 500 characters."
        parsed = llm.parse(user_input)
        return handle_trade_flow(parsed, user_input)

    # Step 2: classify intent ONLY if no active trade
    intent_result = llm.classify_intent(user_input)
    intent = intent_result.get("intent")

    # Step 3: start new trade flow
    if intent == "place_trade":
        parsed = llm.parse(user_input)
        return handle_trade_flow(parsed, user_input)

    if intent == "portfolio_insight":
        return (
            "📊 I’m still building the portfolio insights module.\n\n"
            "Soon you’ll be able to see holdings, performance, and analytics here.\n\n"
            "For now, I can help you **place a trade** if you’d like."
        )

    if intent == "transfer":
        return (
            "💸 Transfers aren’t supported yet, but they’re on the roadmap.\n\n"
            "I can currently help you **buy or sell stocks** if that’s useful."
        )

    if intent == "market_research":
        return (
            "📝 Market research is not available yet.\n\n"
            "Right now, I’m focused on helping you **place trades quickly and accurately**."
        )
    
    if intent == "kyc":
        return (
            "📝 Profile and KYC updates aren’t available yet.\n\n"
            "Right now, I’m focused on helping you **place trades quickly and accurately**."
        )
    
    if intent == "help_faq":
        return (
            "📝 I can't help with common questions about using the platform at this stage.\n\n"
            "Right now, I’m focused on helping you **place trades quickly and accurately**."
        )
    # fallback
    return (
        "I’m not sure I can help with that yet.\n\n"
        "You can try something like:\n"
        "- *Buy 10 shares of AAPL*\n"
        "- *Sell 5 TSLA at market price*"
    )





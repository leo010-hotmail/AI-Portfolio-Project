from llm import get_llm_client
from orchestration.market_data_flow import handle_market_data_flow
from orchestration.market_research_flow import handle_market_research_flow
from orchestration.orders_flow import handle_view_orders_flow
from orchestration.portfolio_flow import handle_view_portfolio_flow
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

    if trade_state and trade_state.get("flow") == "market_data":
        if len(user_input) > MAX_CHARS:
            return "Please keep your message under 500 characters."
        parsed = llm.parse(user_input)
        return handle_market_data_flow(parsed, user_input)

    if trade_state and trade_state.get("flow") == "market_research":
        return handle_market_research_flow(user_input)

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
        st.session_state.trade_state = {"flow": "place_trade"}
        parsed = llm.parse(user_input)
        return handle_trade_flow(parsed, user_input)

    if intent == "cancel_order":
        st.session_state.trade_state = {"flow": "cancel_order"}
        parsed = llm.parse(user_input)
        return handle_trade_flow(parsed, user_input)

    if intent == "market_data":
        st.session_state.trade_state = {"flow": "market_data"}
        parsed = llm.parse(user_input)
        return handle_market_data_flow(parsed, user_input)

    if intent == "market_research":
        st.session_state.trade_state = {"flow": "market_research"}
        return handle_market_research_flow(user_input)

    if intent == "view_orders":
        return handle_view_orders_flow()

    if intent == "view_portfolio":
        return handle_view_portfolio_flow()

    if intent == "transfer":
        return (
            "💸 Transfers aren’t supported yet, but they’re on the roadmap.\n\n"
            "I can currently help you **buy or sell stocks** if that’s useful.\n"
            "You can try something like:\n"
            "- *Buy 10 shares of AAPL*\n"
            "- *Sell 5 TSLA at market price*\n"
            "- *Cancel order for AAPL*\n"
            "- *Show me my open orders*\n"
            "- *How is my portfolio doing?*\n"
            "- *Show me the current price for MSFT*\n"
            "- *What is the latest news on Tesla*"
        )

    if intent == "kyc":
        return (
            "📝 Profile and KYC updates aren’t available yet.\n\n"
            "Right now, I’m focused on helping you **place trades quickly and accurately**.\n"
            "You can try something like:\n"
            "- *Buy 10 shares of AAPL*\n"
            "- *Sell 5 TSLA at market price*\n"
            "- *Cancel order for AAPL*\n"
            "- *Show me my open orders*\n"
            "- *How is my portfolio doing?*\n"
            "- *Show me the current price for MSFT*\n"
            "- *What is the latest news on Tesla*"
        )
    
    if intent == "help_faq":
        return (
            "📝 I can't help with common questions about using the platform at this stage.\n\n"
            "Right now, I’m focused on helping you **place trades quickly and accurately**.\n"
            "You can try something like:\n"
            "- *Buy 10 shares of AAPL*\n"
            "- *Sell 5 TSLA at market price*\n"
            "- *Cancel order for AAPL*\n"
            "- *Show me my open orders*\n"
            "- *How is my portfolio doing?*\n"
            "- *Show me the current price for MSFT*\n"
            "- *What is the latest news on Tesla*"
        )
    # fallback
    return (
        "I’m not sure I can help with that yet.\n\n"
        "You can try something like:\n"
        "- *Buy 10 shares of AAPL*\n"
        "- *Sell 5 TSLA at market price*\n"
        "- *Cancel order for AAPL*\n"
        "- *Show me my open orders*\n"
        "- *How is my portfolio doing?*\n"
        "- *Show me the current price for MSFT*\n"
        "- *What is the latest news on Tesla*"
    )





import streamlit as st
from orchestration.orchestrator import handle_user_input
from services.broker_app import list_accounts, get_account,load_account_snapshot
#from services.trading_app import get_account_snapshot

import time

MAX_REQUESTS = 20
WINDOW_SECONDS = 60

if "request_times" not in st.session_state:
    st.session_state.request_times = []

now = time.time()

# keep only recent requests
st.session_state.request_times = [
    t for t in st.session_state.request_times
    if now - t < WINDOW_SECONDS
]

if len(st.session_state.request_times) >= MAX_REQUESTS:
    st.warning("⚠️ Too many requests. Please wait a minute.")
    st.stop()

st.session_state.request_times.append(now)


st.title("AI Investment Assistant - v1.0a")

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "trade_state" not in st.session_state:
    st.session_state.trade_state = {}


# ---------- Account Snapshot (load once per session) ----------
if "account_snapshot" not in st.session_state:
    try:
        st.session_state.account_snapshot = load_account_snapshot()
    except Exception as e:
        st.session_state.account_snapshot = None
        st.sidebar.error("Failed to load account snapshot")

with st.sidebar:
    st.header("📊 Account Snapshot")

    snapshot = st.session_state.get("account_snapshot")

    if snapshot:
        st.markdown("**Account**")
        st.write(snapshot["account_number"])

        st.markdown("**Account Type**")
        st.write(snapshot["account_type"])

        st.metric("Equity", f"${snapshot['last_equity']}")


    else:
        st.info("Account data not available")        
# ---------- Render Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------- Chat Input ----------
user_input = st.chat_input("What would you like to do today?")


if user_input:
    # 1️⃣ Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 2️⃣ Get assistant response
    response = handle_user_input(user_input)

    # 3️⃣ Save assistant response (ONLY if non-empty)
    if response:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

    # 4️⃣ Force rerender
    st.rerun()

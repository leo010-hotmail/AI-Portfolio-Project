import streamlit as st
from orchestration.orchestrator import handle_user_input

st.title("AI Investment Assistant")

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "trade_state" not in st.session_state:
    st.session_state.trade_state = {}

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

import streamlit as st
from orchestration.orchestrator import handle_user_input
from services.broker_app import get_trading_account_details, list_accounts, get_account, list_orders, list_positions
from services.logger import log_message
import plotly.graph_objects as go

import time

MAX_REQUESTS = 20
WINDOW_SECONDS = 60
def render_price_chart(symbol: str, df):
    if df is None or df.empty:
        st.warning("No historical data available to render the chart.")
        return

    if "c" not in df:
        st.warning("Historical data is missing closing prices.")
        return

    df = df.sort_index()
    min_price = df["c"].min()
    max_price = df["c"].max()

    padding = (max_price - min_price) * 0.05 if min_price is not None and max_price is not None else 0.0

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["c"],
        mode="lines",
        name="Close Price"
    ))

    fig.update_layout(
        title=f"{symbol} - Last 30 Days",
        yaxis=dict(
            range=[
                min_price - padding,
                max_price + padding
            ]
        ),
        xaxis_title="Date",
        yaxis_title="Price",
    )

    st.plotly_chart(fig, use_container_width=True)

def load_sidebar_data():
    try:
        accounts = list_accounts()
        account_id = accounts[0]["id"]

        st.session_state.account_snapshot = get_account(account_id)
        st.session_state.trading_account = get_trading_account_details(account_id)
        st.session_state.recent_orders = list_orders(account_id, limit=5)
        st.session_state.positions = list_positions(account_id)

    except Exception:
        st.session_state.account_snapshot = None
        st.session_state.recent_orders = []
        st.session_state.positions = []

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
st.markdown("###### Trade, view orders, analyse portfolio, check stock quotes, monitor market news")

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "trade_state" not in st.session_state:
    st.session_state.trade_state = {}

if "show_market_data_chart" not in st.session_state:
    st.session_state.show_market_data_chart = False


# ---------- Account Snapshot (load once per session) ----------
if "sidebar_loaded" not in st.session_state:
    load_sidebar_data()
    st.session_state.sidebar_loaded = True
#    try:
#        accounts = list_accounts()
#        account_id = accounts[0]["id"]
    
#        st.session_state.account_snapshot = get_account(account_id)
#        st.session_state.trading_account = get_trading_account_details(account_id)

#    except Exception as e:
#        st.session_state.account_snapshot = None
#        st.sidebar.error("Failed to load account snapshot")

with st.sidebar:
    if st.button("🔄 Refresh"):
        load_sidebar_data()
        st.rerun()

    st.header("📊 Account Snapshot")

    snapshot = st.session_state.get("account_snapshot")

    if snapshot:
        trading_account = st.session_state.get("trading_account")

        st.markdown("**Account**")
        st.write(snapshot["account_number"])

        st.markdown("**Equity**")
        last_equity = float(snapshot.get("last_equity", 0))
        st.write(f"${last_equity:,.2f}")

        #st.write(f"${snapshot['last_equity']}")

        if trading_account:
            buying_power = float(trading_account.get("buying_power", 0))

            st.markdown("**Buying Power**")
            st.write(f"${buying_power:,.2f}")

    else:
        st.info("Account data not available")    

# ---------- Recent Order  ----------
# Get account ID
#accounts = list_accounts()
#account_id = accounts[0]["id"]

# Fetch 5 most recent orders
#orders = list_orders(account_id, limit=5)
orders = st.session_state.get("recent_orders", [])

st.sidebar.markdown("### 🧾 Recent Orders")

if not orders:
    st.sidebar.write("No recent orders.")
else:
    for order in orders:
        symbol = order.get("symbol")
        qty = order.get("qty")
        status = order.get("status")

        st.sidebar.write(
            f"**{symbol}** — {qty} shares\nStatus: `{status}`"
        )

# ---------- Top holdings  ----------
def render_top_holdings():
    positions = st.session_state.get("positions", [])

    if not positions:
        st.sidebar.markdown("### 📊 Top Holdings")
        st.sidebar.write("No positions yet.")
        return

    sorted_positions = sorted(
        positions,
        key=lambda x: float(x.get("market_value", 0)),
        reverse=True
    )

    top_5 = sorted_positions[:5]

    st.sidebar.markdown("### 📊 Top Holdings")

    for pos in top_5:
        symbol = pos["symbol"]
        qty = pos["qty"]
        market_value = float(pos["market_value"])

        st.sidebar.write(
            f"**{symbol}** — {qty} shares  \n"
            f"Market value: ${market_value:,.2f}"
        )
render_top_holdings()
# ---------- Render Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

    # --------- Render History Chart ------------
    if (
        msg["role"] == "assistant"
        and st.session_state.get("show_market_data_chart")
        and "last_chart" in st.session_state
        and msg["content"].startswith("### Market Update")
    ):
        render_price_chart(
            st.session_state.last_chart_symbol,
            st.session_state.last_chart
        )

# ---------- Chat Input ----------
user_input = st.chat_input("What would you like to do today?")



if user_input:
    #st.session_state.show_market_data_chart = False
    # 1️⃣ Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # ✅ Log user message immediately
    log_message("user", user_input, session_id=st.session_state.get("session_id", "session1"))

    # 2️⃣ Get assistant response
    response = handle_user_input(user_input)

    # 3️⃣ Save assistant response (ONLY if non-empty)
    if response:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

    # ✅ Log assistant response immediately
    log_message("assistant", response, session_id=st.session_state.get("session_id", "session1"))

    # 4️⃣ Force rerender
    st.rerun()

# ---------- Footer ----------
with st.sidebar:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center; font-size:12px; color:gray;">
        Built by <b>Aman A.</b><br>
        Powered by <b>OpenAI</b>, <b>Alpaca</b> and <b>Perigon</b>.<br>
        Interactions may be logged for product improvement.
        </div>
        """,
        unsafe_allow_html=True
    )


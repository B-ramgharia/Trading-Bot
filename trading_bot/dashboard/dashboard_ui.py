import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="Binance Trading Bot Dashboard",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff9900;
        color: white;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3e4451;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State for Auth
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

def login(username, password):
    try:
        response = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            # Get user info
            me_resp = requests.get(f"{API_URL}/auth/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
            st.session_state.user = me_resp.json()
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

def signup(username, password):
    try:
        response = requests.post(f"{API_URL}/auth/signup", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Account created! Please log in.")
            return True
        else:
            st.error(f"Signup failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

# --- UI LOGIC ---

@st.cache_data(ttl=3600)
def get_symbols():
    try:
        resp = requests.get(f"{API_URL}/exchange-info")
        if resp.status_code == 200:
            return [s["symbol"] for s in resp.json()["symbols"]]
    except:
        pass
    return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]

def cancel_order(symbol, order_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        resp = requests.delete(f"{API_URL}/order", json={"symbol": symbol, "order_id": order_id}, headers=headers)
        if resp.status_code == 200:
            st.success(f"Order {order_id} cancelled.")
            return True
        else:
            st.error(f"Cancel failed: {resp.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {e}")
    return False

if st.session_state.token is None:
    st.title("🤖 Binance Trading Bot")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Log In"):
                if login(user, pw):
                    st.rerun()
    
    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("New Username")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Sign Up"):
                if new_pw != confirm_pw:
                    st.error("Passwords do not match")
                else:
                    signup(new_user, new_pw)

else:
    # Authenticated View
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    st.title("📈 Trading Dashboard")

    # --- Metrics Section ---
    m1, m2, m3, m4 = st.columns(4)
    
    try:
        # Mocking or fetching metrics from API
        # This will need real backend connection to Binance client via FastAPI
        acc_resp = requests.get(f"http://127.0.0.1:8000/api/account", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if acc_resp.status_code == 200:
            data = acc_resp.json()
            m1.metric("Wallet Balance", f"${float(data.get('totalWalletBalance', 0)):,.2f}")
            m2.metric("Available", f"${float(data.get('availableBalance', 0)):,.2f}")
            m3.metric("Unrealized PnL", f"${float(data.get('totalUnrealizedProfit', 0)):,.2f}")
            m4.metric("Active Positions", len(data.get("positions", [])))
        else:
            st.warning("Could not fetch real-time account data. Ensure API keys are set in .env")
    except:
        st.error("Error connecting to backend API. Is uvicorn running?")

    # --- Main Content ---
    tabs = st.tabs(["🚀 Terminal", "📊 Positions", "📓 Trade Journal", "📈 Analysis"])

    with tabs[0]:
        st.subheader("New Order")
        c1, c2 = st.columns(2)
        with c1:
            all_symbols = get_symbols()
            symbol = st.selectbox("Symbol", all_symbols, index=all_symbols.index("BTCUSDT") if "BTCUSDT" in all_symbols else 0)
            side = st.radio("Side", ["BUY", "SELL"], horizontal=True)
            order_type = st.selectbox("Type", ["MARKET", "LIMIT", "STOP_MARKET", "STOP"])
        
        with c2:
            qty = st.number_input("Quantity", min_value=0.0001, step=0.001, format="%.4f")
            price = None
            stop_price = None
            if order_type in ["LIMIT", "STOP"]:
                price = st.number_input("Price", min_value=0.0, format="%.2f")
            if order_type in ["STOP_MARKET", "STOP"]:
                stop_price = st.number_input("Stop Price", min_value=0.0, format="%.2f")
            
            notes = st.text_area("Journal Notes (Optional)", placeholder="Strategy, emotional state, etc.")

        if st.button("Place Order", use_container_width=True):
            payload = {
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "quantity": qty,
                "price": price,
                "stop_price": stop_price,
                "notes": notes
            }
            res = requests.post(f"{API_URL}/order", json=payload, headers={"Authorization": f"Bearer {st.session_state.token}"})
            if res.status_code == 200:
                st.success(f"Order Placed! ID: {res.json()['order']['orderId']}")
                st.balloons()
            else:
                st.error(f"Error: {res.json().get('detail', 'Unknown error')}")

    with tabs[1]:
        st.subheader("Open Positions")
        try:
            acc_resp = requests.get(f"{API_URL}/account", headers={"Authorization": f"Bearer {st.session_state.token}"})
            if acc_resp.status_code == 200:
                positions = acc_resp.json().get("positions", [])
                if positions:
                    pos_df = pd.DataFrame(positions)
                    # Prettify position names
                    pos_df = pos_df[["symbol", "positionAmt", "entryPrice", "unrealizedProfit", "leverage", "positionSide"]]
                    st.dataframe(pos_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No active positions.")
            else:
                st.error("Failed to fetch positions.")
            
            st.divider()
            st.subheader("Open Orders")
            ord_resp = requests.get(f"{API_URL}/open-orders", headers={"Authorization": f"Bearer {st.session_state.token}"})
            if ord_resp.status_code == 200:
                orders = ord_resp.json().get("orders", [])
                if orders:
                    for o in orders:
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        col1.write(f"**{o['symbol']}** {o['side']} {o['type']}")
                        col2.write(f"Qty: {o['origQty']}")
                        col3.write(f"Price: {o['price']}")
                        if col4.button("Cancel", key=f"can_{o['orderId']}"):
                            if cancel_order(o["symbol"], o["orderId"]):
                                st.rerun()
                else:
                    st.info("No open orders.")
        except:
            st.error("Error connecting to backend.")

    with tabs[2]:
        st.subheader("Your Trade Journal")
        
        # Filters in columns
        f1, f2, f3 = st.columns(3)
        with f1:
            search_symbol = st.text_input("Filter by Symbol", placeholder="e.g. BTC").upper()
        with f2:
            search_side = st.selectbox("Filter by Side", ["All", "BUY", "SELL"])
        with f3:
            search_type = st.selectbox("Filter by Type", ["All", "MARKET", "LIMIT", "STOP", "STOP_MARKET"])

        journal_res = requests.get(f"{API_URL}/journal", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if journal_res.status_code == 200:
            trades = journal_res.json()
            if trades:
                df = pd.DataFrame(trades)
                
                # Apply Filters
                if search_symbol:
                    df = df[df['symbol'].str.contains(search_symbol)]
                if search_side != "All":
                    df = df[df['side'] == search_side]
                if search_type != "All":
                    df = df[df['order_type'] == search_type]

                # Interactive editor
                edited_df = st.data_editor(
                    df, 
                    num_rows="dynamic", 
                    disabled=["id", "created_at", "symbol", "side", "order_type", "quantity", "price", "stop_price", "status", "executed_qty", "avg_price"],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Logic to update notes if edited (simplified for this step)
                if st.button("Save Journal Updates"):
                    st.info("Bulk update logic pending implementation.")
            else:
                st.info("Your journal is empty. Place some trades to see them here!")
        else:
            st.error("Failed to fetch journal.")

    with tabs[3]:
        st.subheader("PnL Performance")
        journal_res = requests.get(f"{API_URL}/journal", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if journal_res.status_code == 200:
            trades = journal_res.json()
            if trades:
                df = pd.DataFrame(trades)
                df['created_at'] = pd.to_datetime(df['created_at'])
                df = df.sort_values('created_at')
                
                # Mock PnL for visualization (Summing unrealized PnL or using avg price diff)
                # For now, let's just show trade volume over time
                fig = px.line(df, x='created_at', y='quantity', color='symbol', 
                             title="Trading Activity (Qty per Trade)", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                # Cumulative Volume chart
                df['cum_qty'] = df['quantity'].cumsum()
                fig2 = px.area(df, x='created_at', y='cum_qty', title="Cumulative Trading Volume", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No data available for analysis.")

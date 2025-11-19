import streamlit as st
import sqlite3
import pandas as pd
import os
import time
import json

# CONFIG
st.set_page_config(page_title="SpiralOS Overwatch", layout="wide")
st.title("🌀 SpiralOS Overwatch")
st.markdown("Constitutional Cognitive Sovereignty | Real-Time Economic Monitoring")

# Live update notice
st.info("💡 **Live Updates**: Dashboard auto-refreshes every 3 seconds. WebSocket API available at http://localhost:8001/ws/events")

# PATHS
BASE_DIR = os.path.join(os.getcwd(), "spiral_data")
ECON_DB = os.path.join(BASE_DIR, "economy.db")
VAULT_DB = os.path.join(BASE_DIR, "vault.db")

def get_supply():
    try:
        conn = sqlite3.connect(ECON_DB)
        cursor = conn.cursor()
        # Correct Schema: economy_meta key='total_supply'
        cursor.execute("SELECT value FROM economy_meta WHERE key='total_supply'")
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row else 0.0
    except Exception as e:
        return 0.0

def get_mint_count():
    try:
        conn = sqlite3.connect(ECON_DB)
        # Correct Schema: mint_events
        df = pd.read_sql_query("SELECT COUNT(*) as count FROM mint_events", conn)
        conn.close()
        return df['count'][0]
    except:
        return 0

def get_feed():
    try:
        conn = sqlite3.connect(ECON_DB)
        # Correct Schema: ts (timestamp), reason (with fallback to context)
        df = pd.read_sql_query(
            "SELECT datetime(ts, 'unixepoch', 'localtime') as Time, "
            "amount as SCAR, "
            "COALESCE(reason, context, 'N/A') as Reason "
            "FROM mint_events ORDER BY ts DESC LIMIT 10", 
            conn
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Feed Error: {e}")
        return pd.DataFrame()

def get_logs():
    try:
        conn = sqlite3.connect(VAULT_DB)
        # Correct Schema: vault_events
        df = pd.read_sql_query("SELECT datetime(ts, 'unixepoch', 'localtime') as Time, event_type as Event, payload_json as Payload FROM vault_events ORDER BY ts DESC LIMIT 10", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Log Error: {e}")
        return pd.DataFrame()

# METRICS
col1, col2 = st.columns(2)
with col1:
    st.metric(label="💰 Total ScarCoin Supply", value=f"{get_supply():.4f}")
with col2:
    st.metric(label="⚡ Total Mints", value=get_mint_count())

# FEED
st.subheader("🔥 The Feed: Recent Transmutations")
st.dataframe(get_feed(), use_container_width=True)

# LOGS
st.subheader("🔐 The Logs: Vault Activity")
st.dataframe(get_logs(), use_container_width=True)

# AUTO REFRESH (The Pulse) - Auto-refresh every 3 seconds
st.markdown("---")
st.markdown("🔄 **Auto-refreshing every 3 seconds...**")
time.sleep(3)
st.rerun()

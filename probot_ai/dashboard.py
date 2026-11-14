import json, sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ProBot AI Monitor", layout="wide")
st.title("ProBot AI — Trading Monitor")
db = Path("data/probot_ai.sqlite3")
if not db.exists():
    st.info("No event database yet. Run the MT5 demo observer first.")
    st.stop()
with sqlite3.connect(db) as con:
    events = pd.read_sql_query("SELECT ts,kind,symbol,payload FROM events ORDER BY id DESC LIMIT 1000", con)
if events.empty:
    st.info("No events recorded yet.")
    st.stop()
events["data"] = events.payload.apply(lambda x: json.loads(x))
risk = events[events.kind == "risk_status"]
signals = events[events.kind.isin(["signal_review","ai_filter_rejected"])]
orders = events[events.kind == "order_result"]
c1,c2,c3 = st.columns(3)
c1.metric("Recorded signal reviews", len(signals))
c2.metric("Executed orders", len(orders))
c3.metric("Latest event", events.iloc[0].kind)
st.subheader("Recent signals and AI decisions")
st.dataframe(signals[["ts","kind","symbol","payload"]], use_container_width=True)
st.subheader("Risk events")
st.dataframe(risk[["ts","payload"]].head(100), use_container_width=True)
st.subheader("Execution log")
st.dataframe(orders[["ts","symbol","payload"]], use_container_width=True)

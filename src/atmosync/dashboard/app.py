from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AtmoSync Dashboard",
    page_icon="🌍",
    layout="wide",
)

# This file lives at src/atmosync/dashboard/app.py, so the project
# root is three levels up. Points at the same DuckDB file every other
# step in the pipeline reads and writes.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "marts" / "atmosync.duckdb"


@st.cache_data
def load_data() -> pd.DataFrame:
    conn = duckdb.connect(database=str(DB_PATH), read_only=True)
    try:
        df = conn.execute("SELECT * FROM mart_spoilage_arbitrage").fetchdf()
    finally:
        conn.close()
    return df


st.title("AtmoSync: Micro-Climate Arbitrage Dashboard")
st.markdown(
    "Real-time monitoring of container micro-climates and "
    "spoilage arbitrage opportunities."
)

st.sidebar.header("Filters & Controls")
threshold = st.sidebar.slider(
    "Minimum Anomaly %", min_value=0.0, max_value=100.0, value=0.0, step=1.0
)

df = load_data()
filtered_df = df[df["anomaly_pct"] >= threshold]

st.subheader("Key Performance Indicators (KPIs)")

total_containers = len(filtered_df)
high_risk_containers = int(filtered_df["arbitrage_flag"].sum()) if not filtered_df.empty else 0
avg_anomaly_pct = round(filtered_df["anomaly_pct"].mean(), 2) if not filtered_df.empty else 0.0

col1, col2, col3 = st.columns(3)
col1.metric("Total Containers", total_containers)
col2.metric("High Risk Containers", high_risk_containers)
col3.metric("Avg Anomaly %", f"{avg_anomaly_pct}%")

st.subheader("Anomaly Percentage by Container")

if not filtered_df.empty:
    chart_df = filtered_df.set_index("container_id")[["anomaly_pct"]]
    st.bar_chart(chart_df)
else:
    st.write("No containers match the current filter.")

st.subheader("Actionable Insights: At-Risk Containers")

action_df = filtered_df[filtered_df["arbitrage_flag"] == True].sort_values(
    "anomaly_pct", ascending=False
)

st.dataframe(action_df, use_container_width=True, hide_index=True)

csv = action_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download At-Risk Containers (CSV)",
    data=csv,
    file_name="at_risk_containers.csv",
    mime="text/csv",
)
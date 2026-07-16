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
st.sidebar.write("Filters coming soon...")

df = load_data()

st.subheader("Raw Data View")
st.dataframe(df, use_container_width=True)
import streamlit as st

st.set_page_config(
    page_title="AtmoSync Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("AtmoSync: Micro-Climate Arbitrage Dashboard")
st.markdown(
    "Real-time monitoring of container micro-climates and "
    "spoilage arbitrage opportunities."
)

st.sidebar.header("Filters & Controls")
st.sidebar.write("Filters coming soon...")

st.info("Data visualizations and metrics will appear here.")
import streamlit as st

# --- App Configuration ---
st.set_page_config(
    page_title="HFMD Malaysia Dashboard",
    page_icon="🦠"
)

# --- Import Pages ---
home = st.Page(
    "home.py",
    title="Temporal & Seasonal Trend",
    icon=":material/insights:",
    default=True
)

visualise = st.Page(
    "hfmd_visualisation.py",
    title="Weather Correlation",
    icon=":material/bar_chart:"
)

# --- Navigation Menu ---
pg = st.navigation(
    {
        "Menu": [home, visualise]
    }
)

pg.run()

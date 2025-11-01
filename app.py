import streamlit as st

st.set_page_config(page_title="HFMD Malaysia Dashboard", page_icon="🦠")

home = st.Page("home.py", title="Temporal & Seasonal Trend", icon=":material/insights:", default=True)
visual = st.Page("hfmd_visualisation.py", title="Weather Correlation", icon=":material/bar_chart:")
regional = st.Page("regional_comparison.py", title="Regional Comparison", icon=":material/map:")

pg = st.navigation({"Menu": [home, visual, regional]})
pg.run()

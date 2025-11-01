import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="HFMD Malaysia Visualization",
    page_icon="🦠"
)

# --- Import Pages ---
home = st.Page(
    'home.py',
    title='Homepage',
    icon=":material/home:",
    default=True
)

visualise = st.Page(
    'hfmd_visualisation.py',
    title='HFMD and Weather Analysis',
    icon=":material/bar_chart:"
)

# --- Navigation Menu ---
pg = st.navigation(
    {
        "Menu": [home, visualise]
    }
)

pg.run()

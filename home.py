import streamlit as st
import pandas as pd

st.subheader("📂 1. Data Loading and Cleaning")

# --- URL to your dataset on GitHub or Mendeley ---
url = "https://raw.githubusercontent.com/<your-repo-name>/<branch>/hfdm_data.csv"

# --- Load and cache ---
@st.cache_data
def load_data(data_url: str) -> pd.DataFrame:
    """Load dataset and cache it."""
    try:
        df = pd.read_csv(data_url)
        return df
    except Exception as e:
        st.error(f"❌ Could not load dataset: {e}")
        return pd.DataFrame()

df_raw = load_data(url)

# --- Validate ---
if df_raw.empty:
    st.error("⚠️ Dataset could not be loaded. Check your URL or file path.")
    st.stop()

# --- Cleaning / renaming example ---
df = df_raw.rename(columns={
    "HFMD Cases": "total_cases",
    "Temperature (°C)": "temp_c",
    "Rainfall (mm)": "rain_c",
    "Relative Humidity (%)": "rh_c",
    # add your actual column names here
})

# --- Date conversion ---
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# --- Drop duplicates / missing values ---
df = df.drop_duplicates(subset="Date")
df = df.dropna(subset=["total_cases"])

# --- Preview ---
st.markdown("**Dataset Preview** (first 5 rows after cleaning)")
st.dataframe(df.head(), use_container_width=True)

# --- Quick summary ---
st.markdown(f"✅ Loaded **{len(df):,}** records from {df['Date'].min().date()} to {df['Date'].max().date()}")
st.markdown("---")

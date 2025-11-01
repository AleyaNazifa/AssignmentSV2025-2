import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. Title ---
st.title("🌦️ HFMD & Weather Correlation Analysis")
st.markdown("---")

# --- 2. Dataset ---
url = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data(url)
if df.empty:
    st.error("Dataset could not be loaded. Please check the URL.")
    st.stop()

df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
df = df.dropna(subset=["date"])

# --- Regions and weather columns ---
region_cols = ["southern", "northern", "central", "east_coast", "borneo"]
weather_cols = ["temp_c", "rain_c", "rh_c"]
df["total_cases"] = df[region_cols].sum(axis=1, numeric_only=True)

# Monthly aggregation
df_m = (
    df.set_index("date")
      .resample("M")
      .mean(numeric_only=True)
      .reset_index()
)
df_m["Year"] = df_m["date"].dt.year
df_m["Month"] = df_m["date"].dt.month

# --- 3. Summary Box ---
def safe_corr(x, y):
    return np.round(df_m[x].corr(df_m[y]), 2) if x in df_m and y in df_m else np.nan

corr_temp = safe_corr("temp_c", "total_cases")
corr_rain = safe_corr("rain_c", "total_cases")
corr_rh = safe_corr("rh_c", "total_cases")

strongest = max(
    [("Temperature", corr_temp), ("Rainfall", corr_rain), ("Humidity", corr_rh)],
    key=lambda x: abs(x[1]) if not np.isnan(x[1]) else -1
)[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temp–HFMD Corr", f"{corr_temp:+.2f}", help="Correlation between temperature and HFMD cases.", border=True)
c2.metric("Rain–HFMD Corr", f"{corr_rain:+.2f}", help="Correlation between rainfall and HFMD cases.", border=True)
c3.metric("RH–HFMD Corr", f"{corr_rh:+.2f}", help="Correlation between humidity and HFMD cases.", border=True)
c4.metric("Strongest Factor", strongest, help="Most influential weather factor on HFMD trends.", border=True)
st.markdown("---")

# --- 4. Visualization 1: Temperature vs HFMD ---
st.header("1. Temperature vs HFMD Cases")
fig1 = px.scatter(df_m, x="temp_c", y="total_cases", trendline="ols",
                  labels={"temp_c": "Temperature (°C)", "total_cases": "Total HFMD Cases"},
                  title="Temperature vs HFMD Cases (Monthly Average)")
st.plotly_chart(fig1, use_container_width=True)
st.info("**Interpretation:** A strong positive correlation suggests higher temperatures coincide with increased HFMD transmission.")

# --- 5. Visualization 2: Humidity vs HFMD ---
st.header("2. Humidity vs HFMD Cases")
fig2 = px.scatter(df_m, x="rh_c", y="total_cases", trendline="ols",
                  labels={"rh_c": "Relative Humidity (%)", "total_cases": "Total HFMD Cases"},
                  title="Humidity vs HFMD Cases (Monthly Average)")
st.plotly_chart(fig2, use_container_width=True)
st.info("**Interpretation:** Moderate positive correlation indicates humid conditions may support HFMD spread.")

# --- 6. Visualization 3: Correlation Matrix ---
st.header("3. Correlation Matrix: Weather & HFMD")
corr_cols = ["temp_c", "rain_c", "rh_c", "total_cases"]
corr_matrix = df_m[corr_cols].corr(numeric_only=True)
fig3 = px.imshow(corr_matrix, text_auto=".2f", aspect="auto",
                 color_continuous_scale="RdBu_r",
                 title="Correlation Matrix between Weather Parameters & HFMD Cases")
st.plotly_chart(fig3, use_container_width=True)
st.info("**Interpretation:** Temperature shows the strongest correlation with HFMD, while rainfall shows weaker association.")

st.success("✅ Objective 2 complete: Correlation metrics, scatter plots, and heatmap visualized successfully.")

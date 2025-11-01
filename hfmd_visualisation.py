import streamlit as st
import numpy as np
import plotly.express as px
from data_loader import load_monthly

st.title("🌦️ HFMD & Weather Correlation")
st.markdown("---")

df_m = load_monthly()

def safe_corr(x, y):
    return float(df_m[[x,y]].dropna().corr().iloc[0,1]) if x in df_m and y in df_m else np.nan

corr_temp = safe_corr("temp_c","total_cases")
corr_rain = safe_corr("rain_c","total_cases")
corr_rh   = safe_corr("rh_c","total_cases")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Temp–HFMD Corr", f"{corr_temp:+.2f}", border=True)
c2.metric("Rain–HFMD Corr", f"{corr_rain:+.2f}", border=True)
c3.metric("RH–HFMD Corr",   f"{corr_rh:+.2f}", border=True)
strongest = max([("Temperature",abs(corr_temp)),("Rainfall",abs(corr_rain)),("Humidity",abs(corr_rh))], key=lambda x: (x[1] if not np.isnan(x[1]) else -1))[0]
c4.metric("Strongest Factor", strongest, border=True)
st.markdown("---")

st.header("1. Temperature vs HFMD Cases")
fig1 = px.scatter(df_m, x="temp_c", y="total_cases",
                  labels={"temp_c":"Temperature (°C)", "total_cases":"Total HFMD Cases"},
                  title="Temperature vs HFMD (Monthly Avg)")
st.plotly_chart(fig1, use_container_width=True)
st.info("Higher temperatures coincide with increased HFMD cases.")

st.header("2. Humidity vs HFMD Cases")
fig2 = px.scatter(df_m, x="rh_c", y="total_cases",
                  labels={"rh_c":"Relative Humidity (%)", "total_cases":"Total HFMD Cases"},
                  title="Humidity vs HFMD (Monthly Avg)")
st.plotly_chart(fig2, use_container_width=True)
st.info("Moderate positive association with humidity.")

st.header("3. Correlation Matrix")
corr_cols = [c for c in ["temp_c","rain_c","rh_c","total_cases"] if c in df_m.columns]
fig3 = px.imshow(df_m[corr_cols].corr(), text_auto=".2f", aspect="auto",
                 color_continuous_scale="RdBu_r",
                 title="Correlation Matrix: Weather vs HFMD")
st.plotly_chart(fig3, use_container_width=True)
st.info("Temperature tends to show the strongest link.")

# hfmd_visualisation.py
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
except ModuleNotFoundError:
    raise SystemExit(
        "Missing packages. Ensure requirements.txt includes:\n"
        "streamlit==1.39.0\npandas==2.2.2"
    )

st.title("🌦️ Objective 2: Weather Correlation with HFMD (2009–2019)")
st.markdown("---")

st.subheader("🎯 Objective Statement")
st.write(
    "Investigate how **temperature**, **humidity**, and **rainfall** relate to monthly **HFMD cases** in Malaysia "
    "from 2009–2019, and identify which weather factor shows the strongest association."
)
st.markdown("---")

# ------------------ LOAD & PREP DATA (monthly) ------------------
DATA_URL = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

@st.cache_data(show_spinner=False)
def load_monthly(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # date
    if "date" not in df.columns:
        raise ValueError("CSV must contain a 'Date' column.")
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    # regions & weather columns (central weather used as representative)
    regions = ["southern", "northern", "central", "east_coast", "borneo"]
    for r in regions:
        if r not in df.columns:
            raise ValueError(f"Missing region column: {r}")

    # allow both rh_c vs rh_central naming styles etc.
    # expected: temp_c, rain_c, rh_c
    # if not present, try alternative keys
    def pick(col_candidates):
        for c in col_candidates:
            if c in df.columns:
                return c
        return None

    temp_key = pick(["temp_c", "temperature_c", "temp_central", "temp_cen"])
    rain_key = pick(["rain_c", "rainfall_c", "rain_central", "rain_cen"])
    rh_key   = pick(["rh_c", "humidity_c", "rh_central", "rh_cen"])

    if temp_key is None or rain_key is None or rh_key is None:
        missing = [n for n,k in {"temp_c":temp_key,"rain_c":rain_key,"rh_c":rh_key}.items() if k is None]
        raise ValueError(f"Missing weather columns (central): {missing} "
                         f"(expected something like temp_c, rain_c, rh_c).")

    # targets
    df["total_cases"] = df[regions].sum(axis=1, numeric_only=True)

    # monthly mean
    m = (
        df.set_index("date")
          .resample("M")
          .mean(numeric_only=True)
          .reset_index()
          .rename(columns={"date": "Date"})
    )
    m["Year"] = m["Date"].dt.year
    m["Month"] = m["Date"].dt.month

    # keep only needed columns for obj2
    m = m[["Date","Year","Month","total_cases", temp_key, rain_key, rh_key]]
    m = m.rename(columns={temp_key:"temp_c", rain_key:"rain_c", rh_key:"rh_c"})
    return m

try:
    df_m = load_monthly(DATA_URL)
except Exception as e:
    st.error(f"❌ Unable to load dataset: {e}")
    st.stop()

# ------------------ SUMMARY BOX (3 METRICS) ------------------
def safe_corr(a, b):
    s = df_m[[a, b]].dropna()
    return float(s.corr().iloc[0,1]) if len(s) > 2 else np.nan

corr_temp = safe_corr("temp_c", "total_cases")
corr_rain = safe_corr("rain_c", "total_cases")
corr_rh   = safe_corr("rh_c",   "total_cases")

strongest = max(
    [("Temperature", corr_temp), ("Rainfall", corr_rain), ("Humidity", corr_rh)],
    key=lambda x: abs(x[1]) if not np.isnan(x[1]) else -1
)[0]

st.subheader("📊 Summary Box")
c1, c2, c3 = st.columns(3)
c1.metric("🌡️ Temp–HFMD Corr", f"{corr_temp:+.2f}",
          help="Pearson correlation between monthly average temperature (central) and total HFMD cases.", border=True)
c2.metric("💧 RH–HFMD Corr", f"{corr_rh:+.2f}",
          help="Pearson correlation between monthly average relative humidity (central) and total HFMD cases.", border=True)
c3.metric("🏆 Strongest Factor", strongest,
          help="Weather variable with the strongest absolute correlation to HFMD.", border=True)
st.markdown("---")

# ------------------ DATA PREVIEW ------------------
with st.expander("🔎 Data Preview (Monthly)"):
    st.dataframe(df_m.head(), use_container_width=True)
    st.caption(f"Rows: {len(df_m):,} • Years: {df_m['Year'].min()}–{df_m['Year'].max()}")

# ------------------ VIZ 1: Temp vs HFMD (scatter + regression) ------------------
st.header("1) Temperature vs HFMD Cases (Monthly)")
st.vega_lite_chart(
    df_m.rename(columns={"total_cases":"TotalCases", "temp_c":"TempC"}),
    {
        "transform": [
            {"regression": "TotalCases", "on": "TempC", "as": ["TempC", "fit"]}
        ],
        "layer": [
            {
                "mark": {"type": "point", "filled": True, "opacity": 0.6},
                "encoding": {
                    "x": {"field": "TempC", "type": "quantitative", "title": "Temperature (°C)"},
                    "y": {"field": "TotalCases", "type": "quantitative", "title": "Total HFMD Cases"},
                    "tooltip": [
                        {"field": "Year", "type": "ordinal"},
                        {"field": "Month", "type": "ordinal"},
                        {"field": "TempC", "type": "quantitative"},
                        {"field": "TotalCases", "type": "quantitative"}
                    ]
                }
            },
            {
                "mark": {"type": "line", "color": "black"},
                "encoding": {
                    "x": {"field": "TempC", "type": "quantitative"},
                    "y": {"field": "fit", "type": "quantitative"}
                }
            }
        ]
    },
    use_container_width=True,
)
st.info("**Interpretation:** Positive slope indicates **higher temperatures tend to coincide with higher HFMD cases**.")

st.markdown("---")

# ------------------ VIZ 2: Humidity vs HFMD (scatter + regression) ------------------
st.header("2) Relative Humidity vs HFMD Cases (Monthly)")
st.vega_lite_chart(
    df_m.rename(columns={"total_cases":"TotalCases", "rh_c":"RH"}),
    {
        "transform": [
            {"regression": "TotalCases", "on": "RH", "as": ["RH", "fit"]}
        ],
        "layer": [
            {
                "mark": {"type": "point", "filled": True, "opacity": 0.6},
                "encoding": {
                    "x": {"field": "RH", "type": "quantitative", "title": "Relative Humidity (%)"},
                    "y": {"field": "TotalCases", "type": "quantitative", "title": "Total HFMD Cases"},
                    "tooltip": [
                        {"field": "Year", "type": "ordinal"},
                        {"field": "Month", "type": "ordinal"},
                        {"field": "RH", "type": "quantitative"},
                        {"field": "TotalCases", "type": "quantitative"}
                    ]
                }
            },
            {
                "mark": {"type": "line", "color": "black"},
                "encoding": {
                    "x": {"field": "RH", "type": "quantitative"},
                    "y": {"field": "fit", "type": "quantitative"}
                }
            }
        ]
    },
    use_container_width=True,
)
st.info("**Interpretation:** A moderate positive slope suggests **humid conditions may support HFMD transmission**.")

st.markdown("---")

# ------------------ VIZ 3: Correlation Heatmap ------------------
st.header("3) Correlation Matrix: Weather vs HFMD")

corr_df = df_m[["total_cases","temp_c","rain_c","rh_c"]].corr(numeric_only=True).reset_index().melt(
    id_vars="index", var_name="Variable", value_name="Correlation"
).rename(columns={"index":"Metric"})

st.vega_lite_chart(
    corr_df,
    {
        "mark": "rect",
        "encoding": {
            "x": {"field": "Variable", "type": "nominal", "title": "Variable"},
            "y": {"field": "Metric", "type": "nominal", "title": "Metric"},
            "color": {
                "field": "Correlation", "type": "quantitative",
                "scale": {"scheme": "redblue", "domain": [-1, 1]},
                "title": "Pearson r"
            },
            "tooltip": [
                {"field": "Metric", "type": "nominal"},
                {"field": "Variable", "type": "nominal"},
                {"field": "Correlation", "type": "quantitative", "format": ".2f"}
            ]
        },
        "width": "container",
        "height": 240
    },
    use_container_width=True,
)
st.info("**Interpretation:** The heatmap summarizes linear relationships; **Temperature** typically shows the strongest association with HFMD, rainfall weaker.")
st.success("✅ Objective 2 complete: 3 metrics + 3 visualizations with interpretations (no Plotly required).")

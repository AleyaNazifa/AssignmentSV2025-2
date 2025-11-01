try:
    import streamlit as st
    import pandas as pd
    import numpy as np
except ModuleNotFoundError:
    raise SystemExit(
        "Missing packages. Ensure requirements.txt includes:\n"
        "streamlit==1.39.0\npandas==2.2.2"
    )

st.title("🗺️ Objective 3: Regional Comparison of HFMD (2009–2019)")
st.markdown("---")

st.subheader("🎯 Objective Statement")
st.write(
    "Compare **HFMD intensity across Malaysian regions** (Southern, Northern, Central, East Coast, Borneo), "
    "identify which regions exhibit higher baselines or variability, and examine **seasonal patterns** by region."
)
st.markdown("---")

# ------------------ LOAD & PREP DATA (monthly) ------------------
DATA_URL = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

@st.cache_data(show_spinner=False)
def load_monthly(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "date" not in df.columns:
        raise ValueError("CSV must contain a 'Date' column in dd/mm/yyyy.")
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    regions = ["southern", "northern", "central", "east_coast", "borneo"]
    missing = [c for c in regions if c not in df.columns]
    if missing:
        raise ValueError(f"Missing region columns: {missing}")

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

    # totals (optional, not used in summary here)
    m["total_cases"] = m[regions].sum(axis=1, numeric_only=True)
    return m

try:
    df_m = load_monthly(DATA_URL)
except Exception as e:
    st.error(f"❌ Unable to load dataset: {e}")
    st.stop()

regions = ["southern", "northern", "central", "east_coast", "borneo"]
region_labels = {
    "southern": "Southern",
    "northern": "Northern",
    "central": "Central",
    "east_coast": "East Coast",
    "borneo": "Borneo",
}

# ------------------ SUMMARY BOX (3 METRICS) ------------------
region_means = df_m[regions].mean()
highest_region_key = region_means.idxmax()
lowest_region_key  = region_means.idxmin()
gap_value = float(region_means.max() - region_means.min())

st.subheader("📊 Summary Box")
c1, c2, c3 = st.columns(3)
c1.metric("🥇 Highest Region", region_labels.get(highest_region_key, highest_region_key).title(),
          help="Region with the highest **average monthly** HFMD cases (2009–2019).", border=True)
c2.metric("🥈 Lowest Region", region_labels.get(lowest_region_key, lowest_region_key).title(),
          help="Region with the lowest **average monthly** HFMD cases (2009–2019).", border=True)
c3.metric("↕️ Case Gap (Avg)", f"{gap_value:.0f}",
          help="Difference between highest and lowest **average monthly** cases across regions.", border=True)
st.markdown("---")

with st.expander("🔎 Data Preview (Monthly)"):
    st.dataframe(df_m[["Date","Year","Month"] + regions].head(), use_container_width=True)
    st.caption(f"Rows (monthly): {len(df_m):,} • Years: {df_m['Year'].min()}–{df_m['Year'].max()}")

# ------------------ VIZ 1: Average Monthly Cases by Region (Bar) ------------------
st.header("1) Average Monthly HFMD Cases by Region")

bar_df = (
    region_means.sort_values(ascending=False)
    .reset_index().rename(columns={"index": "Region", 0: "AvgMonthlyCases"})
)
bar_df["Region"] = bar_df["Region"].map(lambda x: region_labels.get(x, x).title())

st.vega_lite_chart(
    bar_df,
    {
        "mark": {"type": "bar"},
        "encoding": {
            "x": {"field": "Region", "type": "nominal", "title": "Region",
                  "sort": "-y"},
            "y": {"field": "AvgMonthlyCases", "type": "quantitative", "title": "Average Monthly HFMD Cases"},
            "tooltip": [
                {"field": "Region", "type": "nominal"},
                {"field": "AvgMonthlyCases", "type": "quantitative", "format": ".0f"}
            ],
            "color": {"field": "Region", "type": "nominal"}
        },
        "width": "container",
        "height": 340
    },
    use_container_width=True
)
st.info("**Interpretation:** Clear regional differences; the **highest** region has a consistently larger baseline than the **lowest**, indicating uneven spatial burden.")
st.markdown("---")

# ------------------ VIZ 2: Distribution of Monthly Cases by Region (Boxplot) ------------------
st.header("2) Distribution of Monthly HFMD Cases by Region (2009–2019)")

melt_box = df_m.melt(id_vars=["Year","Month","Date"], value_vars=regions,
                     var_name="Region", value_name="Cases")
melt_box["Region"] = melt_box["Region"].map(lambda x: region_labels.get(x, x).title())

st.vega_lite_chart(
    melt_box,
    {
        "mark": "boxplot",
        "encoding": {
            "x": {"field": "Region", "type": "nominal", "title": "Region", "sort": "y"},
            "y": {"field": "Cases", "type": "quantitative", "title": "Monthly HFMD Cases"},
            "color": {"field": "Region", "type": "nominal"},
            "tooltip": [
                {"field": "Region", "type": "nominal"},
                {"field": "Cases", "type": "quantitative"}
            ]
        },
        "width": "container",
        "height": 360
    },
    use_container_width=True
)
st.info("**Interpretation:** Regions with **higher medians** and **wider IQR** (box width) show greater typical levels and variability of HFMD incidence.")
st.markdown("---")

# ------------------ VIZ 3: Seasonal Pattern by Region (Monthly Climatology, Faceted) ------------------
st.header("3) Seasonal Pattern by Region (Monthly Climatology)")

clim_df = (
    melt_box.groupby(["Region","Month"], as_index=False)["Cases"]
            .mean().rename(columns={"Cases":"AvgMonthlyCases"})
)

st.vega_lite_chart(
    clim_df,
    {
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {
                "field": "Month", "type": "ordinal", "title": "Month",
                "scale": {"domain": list(range(1,13))},
                "axis": {"labelExpr":
                         "['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][datum.value-1]"}
            },
            "y": {"field": "AvgMonthlyCases", "type": "quantitative", "title": "HFMD (Avg Monthly Cases)"},
            "color": {"field": "Region", "type": "nominal"},
            "tooltip": [
                {"field": "Region", "type": "nominal"},
                {"field": "Month", "type": "ordinal"},
                {"field": "AvgMonthlyCases", "type": "quantitative", "format": ".0f"}
            ]
        },
        "facet": {"field": "Region", "type": "nominal", "columns": 2, "title": None},
        "width": 320,
        "height": 220,
        "resolve": {"scale": {"y": "independent"}}
    },
    use_container_width=True
)
st.info("**Interpretation:** All regions show **mid-year peaks**, but amplitude differs; some regions display sharper, more pronounced surges than others.")
st.success("✅ Objective 3 complete: 3 metrics + 3 regional visualizations with interpretations.")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("🦠 Objective 1: Temporal & Seasonal Trend of HFMD in Malaysia (2009–2019)")
st.markdown("---")

# =============== 1) LOAD & CLEAN ===============
st.subheader("📂 1. Data Loading & Cleaning")

# Your GitHub raw CSV URL (fallback if user doesn't upload)
URL_FALLBACK = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

uploaded = st.file_uploader("Upload your HFMD CSV", type=["csv"])

@st.cache_data
def load_csv(file_or_url):
    if hasattr(file_or_url, "read"):
        return pd.read_csv(file_or_url)
    elif isinstance(file_or_url, str) and file_or_url.strip():
        return pd.read_csv(file_or_url.strip())
    return pd.DataFrame()

# choose source
df_raw = load_csv(uploaded if uploaded is not None else URL_FALLBACK)
if df_raw.empty:
    st.error("⚠️ Dataset is empty or unreadable. Please upload a valid CSV or check the URL.")
    st.stop()

# Flexible date column
date_col = None
for cand in ["Date", "date", "DATE"]:
    if cand in df_raw.columns:
        date_col = cand
        break
if not date_col:
    st.error("❌ No 'Date' column found. Please ensure your file has a 'Date' column.")
    st.stop()

# Standardize names (lowercase, underscores) & parse date
df = df_raw.copy()
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
date_col = date_col.lower()
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(by=date_col)

# Required region columns
region_cols = ["southern", "northern", "central", "east_coast", "borneo"]
missing = [c for c in region_cols if c not in df.columns]
if missing:
    st.error(f"❌ Missing region columns: {missing}")
    st.stop()

# Compute total cases, drop dups
df["total_cases"] = df[region_cols].sum(axis=1, numeric_only=True)
df = df.drop_duplicates(subset=[date_col])

# Monthly aggregation (for Objective 1)
df_monthly = (
    df.set_index(date_col)
      .resample("M")
      .mean(numeric_only=True)
      .reset_index()
      .rename(columns={date_col: "Date"})
)
df_monthly["Year"]  = df_monthly["Date"].dt.year
df_monthly["Month"] = df_monthly["Date"].dt.month

# Preview
st.markdown("**Dataset Preview (after cleaning)**")
st.dataframe(df.head(), use_container_width=True)
st.caption(f"Daily rows: {len(df):,} · Range: {df['Date'].min().date()} — {df['Date'].max().date()}")

st.markdown("**Monthly aggregation**")
st.dataframe(df_monthly.head(), use_container_width=True)
st.caption(f"Monthly rows: {len(df_monthly):,} · Years: {df_monthly['Year'].min()}—{df_monthly['Year'].max()}")
st.markdown("---")

# =============== 2) SUMMARY BOX ===============
st.subheader("📊 Summary Box")
c1, c2, c3, c4 = st.columns(4, gap="large")

avg_monthly = float(df_monthly["total_cases"].mean())
peak_year = int(df_monthly.groupby("Year")["total_cases"].mean().idxmax())

# top 3 seasonal months by mean
month_means = df_monthly.groupby("Month")["total_cases"].mean().sort_values(ascending=False)
top_months = month_means.head(3).index.tolist()
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
seasonal_peak = "–".join(month_names[m-1] for m in sorted(top_months)) if top_months else "—"

coverage = f"{df_monthly['Year'].min()}–{df_monthly['Year'].max()}"

c1.metric("Avg monthly cases", f"{avg_monthly:.0f}",
          help="Mean HFMD cases per month across all regions.", border=True)
c1.caption("Mean across months")

c2.metric("Peak year", f"{peak_year}",
          help="Year with the highest average monthly HFMD cases.", border=True)
c2.caption("Highest annual average")

c3.metric("Seasonal peak", seasonal_peak,
          help="Months that most often recorded the highest HFMD activity.", border=True)
c3.caption("Typical outbreak window")

c4.metric("Coverage", coverage,
          help="Temporal coverage of the dataset used here.", border=True)
c4.caption("Dataset period")

st.markdown("---")

# =============== 3) VISUALIZATIONS (3) ===============
st.subheader("📈 2. Visualizations")

# 1) Line Trend: Monthly total cases
st.markdown("#### Visualization 1: Monthly HFMD Cases Trend")
fig1 = px.line(
    df_monthly,
    x="Date", y="total_cases",
    labels={"Date": "Year", "total_cases": "Average Monthly Cases"},
    title="Monthly Trend of HFMD Cases (2009–2019)",
    line_shape="spline"
)
st.plotly_chart(fig1, use_container_width=True)
st.caption("The line chart shows cyclical rises and falls in HFMD cases, with visible peaks in certain months each year.")

# 2) Bar: Average yearly HFMD cases
st.markdown("#### Visualization 2: Average Yearly HFMD Cases")
yearly_avg = df_monthly.groupby("Year")["total_cases"].mean().reset_index()
fig2 = px.bar(
    yearly_avg, x="Year", y="total_cases",
    labels={"total_cases": "Average Monthly Cases"},
    color="total_cases", color_continuous_scale="Reds",
    title="Average Yearly HFMD Cases (2009–2019)"
)
st.plotly_chart(fig2, use_container_width=True)
st.caption("Yearly averages highlight which years had higher overall incidence, useful for long-term comparisons.")

# 3) Heatmap: Seasonal pattern (Month × Year)
st.markdown("#### Visualization 3: Seasonal Pattern Heatmap (Month × Year)")
pivot = df_monthly.pivot_table(values="total_cases", index="Month", columns="Year", aggfunc="mean")
fig3 = px.imshow(
    pivot, aspect="auto", origin="lower",
    color_continuous_scale="YlOrRd",
    labels=dict(x="Year", y="Month", color="Avg Monthly Cases"),
    title="Seasonal Heatmap of HFMD Cases"
)
# nicer y-axis ticks
fig3.update_yaxes(tickmode="array", tickvals=list(range(1,13)),
                  ticktext=month_names)
st.plotly_chart(fig3, use_container_width=True)
st.caption("The heatmap reveals consistent seasonal surges (often mid-year), and how intensity varies by year.")

# =============== 4) INTERPRETATION ===============
st.subheader("🧠 3. Interpretation / Discussion")
st.write(
    "Across 2009–2019, HFMD shows **recurring seasonal peaks**, typically clustered in **mid-year months**. "
    "Yearly averages indicate certain years (e.g., the peak year) with elevated incidence. "
    "These temporal and seasonal patterns support **early-warning planning** and targeted health campaigns "
    "ahead of the usual outbreak window."
)
st.success("✅ Objective 1 complete: data prepared, 3 visuals shown, interpretation provided.")

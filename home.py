import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Page Configuration & Title ---
st.title("🦠 HFMD Malaysia: Temporal & Seasonal Trend (2009–2019)")
st.markdown("---")

# --- 2. Dataset Loading & Cleaning ---
url = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

@st.cache_data
def load_data(data_url: str) -> pd.DataFrame:
    try:
        data = pd.read_csv(data_url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

raw_df = load_data(url)

if raw_df.empty:
    st.error("Data could not be loaded. Please check the URL and file.")
    st.stop()

df = raw_df.copy()
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Detect date column
date_col = "date" if "date" in df.columns else None
if not date_col:
    st.error("❌ 'Date' column not found.")
    st.stop()

df[date_col] = pd.to_datetime(df[date_col], format="%d/%m/%Y", errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(by=date_col)

# Expected region columns
region_cols = ["southern", "northern", "central", "east_coast", "borneo"]
missing = [c for c in region_cols if c not in df.columns]
if missing:
    st.error(f"Missing region columns: {missing}")
    st.stop()

# Compute total HFMD cases
df["total_cases"] = df[region_cols].sum(axis=1, numeric_only=True)

# Monthly aggregation
df_m = (
    df.set_index(date_col)
      .resample("M")
      .mean(numeric_only=True)
      .reset_index()
      .rename(columns={date_col: "Date"})
)
df_m["Year"] = df_m["Date"].dt.year
df_m["Month"] = df_m["Date"].dt.month

# --- 3. Summary Box ---
avg_monthly = df_m["total_cases"].mean()
peak_year = df_m.groupby("Year")["total_cases"].mean().idxmax()
month_means = df_m.groupby("Month")["total_cases"].mean().sort_values(ascending=False)
top_months = month_means.head(3).index.tolist()
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
seasonal_peak = "–".join(month_names[m-1] for m in sorted(top_months))
coverage = f"{df_m['Year'].min()}–{df_m['Year'].max()}"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Monthly Cases", f"{avg_monthly:.0f}", help="Mean monthly HFMD cases.", border=True)
col2.metric("Peak Year", f"{int(peak_year)}", help="Year with the highest average HFMD cases.", border=True)
col3.metric("Seasonal Peak", seasonal_peak, help="Months that record the highest HFMD cases.", border=True)
col4.metric("Coverage", coverage, help="Dataset coverage period.", border=True)
st.markdown("---")

# --- 4. Data Preview ---
st.header("1. Data Preview")
st.dataframe(df.head(), use_container_width=True)
st.caption(f"Daily rows: {len(df):,} | Range: {df['date'].min().date()} — {df['date'].max().date()}")
st.markdown("---")

# --- 5. Visualization 1: Monthly Trend ---
st.header("2. Monthly HFMD Cases Trend")
fig1 = px.line(
    df_m, x="Date", y="total_cases",
    title="Monthly Trend of HFMD Cases (2009–2019)",
    labels={"Date": "Year", "total_cases": "Average Monthly Cases"},
    line_shape="spline"
)
st.plotly_chart(fig1, use_container_width=True)
st.info("**Interpretation:** Cyclical mid-year peaks indicate strong seasonal trends in HFMD transmission.")
st.markdown("---")

# --- 6. Visualization 2: Average Yearly Cases ---
st.header("3. Average Yearly HFMD Cases")
yearly_avg = df_m.groupby("Year")["total_cases"].mean().reset_index()
fig2 = px.bar(
    yearly_avg, x="Year", y="total_cases",
    title="Average Yearly HFMD Cases (2009–2019)",
    labels={"total_cases": "Average Monthly Cases"},
    color="total_cases", color_continuous_scale="Reds"
)
st.plotly_chart(fig2, use_container_width=True)
st.info("**Interpretation:** Certain years, especially around the peak, show higher overall HFMD incidence.")
st.markdown("---")

# --- 7. Visualization 3: Seasonal Heatmap ---
st.header("4. Seasonal Pattern (Month × Year)")
pivot = df_m.pivot_table(values="total_cases", index="Month", columns="Year", aggfunc="mean")
fig3 = px.imshow(
    pivot, aspect="auto", origin="lower",
    color_continuous_scale="YlOrRd",
    labels=dict(x="Year", y="Month", color="Avg Monthly Cases"),
    title="Seasonal Heatmap of HFMD Cases"
)
fig3.update_yaxes(tickmode="array", tickvals=list(range(1, 13)), ticktext=month_names)
st.plotly_chart(fig3, use_container_width=True)
st.info("**Interpretation:** Consistent HFMD surges occur in mid-year months, confirming predictable outbreak cycles.")
st.markdown("---")

st.success("✅ Objective 1 complete: data prepared, visuals created, and interpretations provided.")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # for the line chart

# --- 1. Configuration and Data Loading ---
# If this page is launched directly (not via app.py), keep this.
# If you run with app.py + st.Page navigation, comment this out to avoid duplicate page_config.
st.set_page_config(layout="wide", page_title="HFMD Temporal & Seasonal Analysis 📊")

st.title("HFMD Malaysia: Temporal & Seasonal Analysis (2009–2019)")
st.markdown("---")

# URL for the data file (your link)
url = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

# --- Summary Metrics (will be filled after we load & aggregate) ---
# Temporary placeholders so layout matches your example immediately
col1, col2, col3, col4 = st.columns(4)
m1 = col1.metric(label="Avg Monthly Cases", value="—", help="Mean monthly HFMD cases across Malaysia (2009–2019)", border=True)
m2 = col2.metric(label="Peak Year", value="—", help="Year with the highest average monthly HFMD cases", border=True)
m3 = col3.metric(label="Seasonal Peak", value="—", help="Months that most often record the highest HFMD activity", border=True)
m4 = col4.metric(label="Coverage", value="—", help="Temporal coverage of the dataset", border=True)

# --- Cached loader (like your example) ---
@st.cache_data
def load_data(data_url: str) -> pd.DataFrame:
    """Loads the data from the URL and caches it to prevent reloading."""
    try:
        df = pd.read_csv(data_url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty on error

raw_df = load_data(url)

if raw_df.empty:
    st.error("Data could not be loaded. Please check the URL and file.")
    st.stop()

# --- Light cleaning / normalization (rename to safe lowercase, parse date) ---
df = raw_df.copy()
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Flexible date column detection
date_col = "date" if "date" in df.columns else None
if date_col is None:
    st.error("No 'Date' column found in the CSV. Please ensure a 'Date' column exists.")
    st.stop()

# Parse date safely (the original CSV uses dd/mm/yyyy)
df[date_col] = pd.to_datetime(df[date_col], format="%d/%m/%Y", errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(by=date_col)

# Region columns expected from your HFMD file
region_cols = ["southern", "northern", "central", "east_coast", "borneo"]
missing_regions = [c for c in region_cols if c not in df.columns]
if missing_regions:
    st.error(f"Missing region columns: {missing_regions}")
    st.stop()

# Total cases across regions
df["total_cases"] = df[region_cols].sum(axis=1, numeric_only=True)

# Monthly aggregation for temporal/seasonal analysis
df_m = (
    df.set_index(date_col)
      .resample("M")
      .mean(numeric_only=True)
      .reset_index()
      .rename(columns={date_col: "Date"})
)
df_m["Year"] = df_m["Date"].dt.year
df_m["Month"] = df_m["Date"].dt.month

# --- Fill Summary Metrics with real values ---
avg_monthly = df_m["total_cases"].mean()
peak_year = df_m.groupby("Year")["total_cases"].mean().idxmax()

month_means = df_m.groupby("Month")["total_cases"].mean().sort_values(ascending=False)
top_months = month_means.head(3).index.tolist()
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
seasonal_peak = "–".join(month_names[m-1] for m in sorted(top_months)) if top_months else "—"

coverage = f"{df_m['Year'].min()}–{df_m['Year'].max()}"

col1.metric(label="Avg Monthly Cases", value=f"{avg_monthly:.0f}",
            help="Mean monthly HFMD cases across Malaysia (2009–2019)", border=True)
col2.metric(label="Peak Year", value=f"{int(peak_year)}",
            help="Year with the highest average monthly HFMD cases", border=True)
col3.metric(label="Seasonal Peak", value=seasonal_peak,
            help="Months that most often record the highest HFMD activity", border=True)
col4.metric(label="Coverage", value=coverage,
            help="Temporal coverage of the dataset", border=True)

# --- 1. Data Preview (like your example) ---
st.header("1. Data Preview")
st.markdown("Displaying the first few rows of the dataset **after basic cleaning**.")
st.dataframe(df.head(), use_container_width=True)
st.markdown("---")

# --- 2. Monthly Trend (Line) ---
st.header("2. Monthly HFMD Cases Trend")
try:
    fig_trend = px.line(
        df_m,
        x="Date", y="total_cases",
        title="Monthly Trend of HFMD Cases (2009–2019)",
        labels={"Date": "Year", "total_cases": "Average Monthly Cases"},
        line_shape="spline"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.info("""
**Interpretation:** The time series shows **cyclical rises and falls** in HFMD cases with clear **mid-year peaks** in many years, indicating strong seasonality in transmission.
""")
except Exception as e:
    st.warning(f"Could not generate Monthly Trend chart: {e}")

st.markdown("---")

# --- 3. Average Yearly Cases (Bar) ---
st.header("3. Average Yearly HFMD Cases")
try:
    yearly_avg = df_m.groupby("Year")["total_cases"].mean().reset_index()
    fig_year = px.bar(
        yearly_avg,
        x="Year", y="total_cases",
        title="Average Yearly HFMD Cases (2009–2019)",
        labels={"total_cases": "Average Monthly Cases"},
        color="total_cases",
        color_continuous_scale="Reds"
    )
    fig_year.update_layout(yaxis_title="Average Monthly Cases", xaxis_title="Year")
    st.plotly_chart(fig_year, use_container_width=True)

    st.info("""
**Interpretation:** Some years (e.g., the **peak year** above) exhibit **elevated baseline incidence**, useful for longer-term planning and comparison across years.
""")
except Exception as e:
    st.warning(f"Could not generate Average Yearly chart: {e}")

st.markdown("---")

# --- 4. Seasonal Pattern (Month × Year Heatmap) ---
st.header("4. Seasonal Pattern (Month × Year Heatmap)")
try:
    pivot = df_m.pivot_table(values="total_cases", index="Month", columns="Year", aggfunc="mean")
    fig_heat = px.imshow(
        pivot,
        aspect="auto",
        origin="lower",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Year", y="Month", color="Avg Monthly Cases"),
        title="Seasonal Heatmap of HFMD Cases"
    )
    fig_heat.update_yaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=month_names
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.info("""
**Interpretation:** The heatmap confirms **recurrent mid-year surges** across multiple years, with intensity varying year to year.
""")
except Exception as e:
    st.warning(f"Could not generate Seasonal Heatmap: {e}")

st.markdown("---")
st.success("Analysis complete! All charts and interpretations are now displayed!")

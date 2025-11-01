import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Page Setup ---
st.set_page_config(layout="wide", page_title="Regional HFMD Comparison 🗺️")
st.title("🗺️ Regional Comparison of HFMD in Malaysia (2009–2019)")
st.markdown("---")

# --- 2. Load & Clean Data ---
url = "https://raw.githubusercontent.com/AleyaNazifa/AssignmentSV2025-1/refs/heads/main/hfdm_data%20-%20Upload.csv"

@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data(url)
if df.empty:
    st.error("Data could not be loaded. Please check the URL and try again.")
    st.stop()

df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
df = df.dropna(subset=["date"])
df = df.sort_values("date")

regions = ["southern", "northern", "central", "east_coast", "borneo"]
df["total_cases"] = df[regions].sum(axis=1, numeric_only=True)

# Monthly averages
df_m = (
    df.set_index("date")
      .resample("M")
      .mean(numeric_only=True)
      .reset_index()
)
df_m["Year"] = df_m["date"].dt.year

# --- 3. Summary Box ---
avg_cases = df_m[regions].mean().mean()
highest_region = df_m[regions].mean().idxmax().replace("_", " ").title()
lowest_region = df_m[regions].mean().idxmin().replace("_", " ").title()
region_gap = df_m[regions].mean().max() - df_m[regions].mean().min()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Monthly Cases", f"{avg_cases:.0f}", help="Mean monthly HFMD cases across Malaysia.", border=True)
col2.metric("Highest Region", highest_region, help="Region with the highest average HFMD cases.", border=True)
col3.metric("Lowest Region", lowest_region, help="Region with the lowest HFMD cases.", border=True)
col4.metric("Case Gap", f"{region_gap:.0f}", help="Difference between highest and lowest regional averages.", border=True)

st.markdown("---")

# --- 4. Visualization 1: Average Monthly Cases by Region ---
st.header("1️⃣ Average Monthly HFMD Cases by Region")
region_mean = df_m[regions].mean().sort_values(ascending=False).reset_index()
region_mean.columns = ["Region", "Average_Cases"]

fig1 = px.bar(
    region_mean,
    x="Region",
    y="Average_Cases",
    title="Average Monthly HFMD Cases (2009–2019)",
    color="Region",
    color_discrete_sequence=px.colors.qualitative.Vivid
)
st.plotly_chart(fig1, use_container_width=True)
st.info("""
**Interpretation:**  
Central and Southern Malaysia consistently report higher HFMD incidence than other regions, 
likely due to higher urban population density and childcare center concentrations.
""")
st.markdown("---")

# --- 5. Visualization 2: Yearly Boxplot Distribution ---
st.header("2️⃣ Yearly HFMD Distribution by Region")
melted = df_m.melt(id_vars=["Year"], value_vars=regions, var_name="Region", value_name="Cases")

fig2 = px.box(
    melted,
    x="Region",
    y="Cases",
    color="Region",
    title="Yearly Distribution of HFMD Cases per Region",
)
st.plotly_chart(fig2, use_container_width=True)
st.info("""
**Interpretation:**  
Southern and Central regions show higher median HFMD levels and wider variability across years, 
indicating more frequent outbreaks compared to East Coast and Borneo.
""")
st.markdown("---")

# --- 6. Visualization 3: Radar Chart (Normalized) ---
st.header("3️⃣ Normalized Regional HFMD Pattern")

norm_means = df_m[regions].mean()
min_val, max_val = norm_means.min(), norm_means.max()
normalized = (norm_means - min_val) / (max_val - min_val + 1e-9)
df_radar = pd.DataFrame({"Region": regions, "Normalized": normalized})

fig3 = go.Figure()
fig3.add_trace(go.Scatterpolar(
    r=df_radar["Normalized"].tolist() + [df_radar["Normalized"].iloc[0]],
    theta=[r.title() for r in regions] + [regions[0].title()],
    fill='toself',
    name="HFMD Intensity"
))
fig3.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    title="Normalized Regional HFMD Intensity",
    showlegend=False
)
st.plotly_chart(fig3, use_container_width=True)

st.info("""
**Interpretation:**  
The radar chart highlights clear regional imbalance, 
with the Central and Southern regions consistently exhibiting the strongest normalized HFMD activity levels.
""")
st.markdown("---")

st.success("✅ Objective 3 complete: Regional averages, distributions, and comparative radar plot generated.")

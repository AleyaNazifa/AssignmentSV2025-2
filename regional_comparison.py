import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_monthly

st.title("🗺️ Regional Comparison of HFMD (2009–2019)")
st.markdown("---")

df_m = load_monthly()
regions = ["southern","northern","central","east_coast","borneo"]

avg_cases = df_m[regions].mean().mean()
highest_region = df_m[regions].mean().idxmax().replace("_"," ").title()
lowest_region  = df_m[regions].mean().idxmin().replace("_"," ").title()
region_gap = df_m[regions].mean().max() - df_m[regions].mean().min()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg Monthly Cases", f"{avg_cases:.0f}", border=True)
c2.metric("Highest Region", highest_region, border=True)
c3.metric("Lowest Region", lowest_region, border=True)
c4.metric("Case Gap", f"{region_gap:.0f}", border=True)
st.markdown("---")

st.header("1) Average Monthly Cases by Region")
region_mean = df_m[regions].mean().sort_values(ascending=False).reset_index()
region_mean.columns = ["Region","Average_Cases"]
fig1 = px.bar(region_mean, x="Region", y="Average_Cases", color="Region",
              color_discrete_sequence=px.colors.qualitative.Vivid,
              title="Average Monthly HFMD Cases")
st.plotly_chart(fig1, use_container_width=True)
st.info("Central & Southern tend to be higher than East Coast & Borneo.")
st.markdown("---")

st.header("2) Yearly Distribution by Region")
melted = df_m.melt(id_vars=["Year"], value_vars=regions, var_name="Region", value_name="Cases")
fig2 = px.box(melted, x="Region", y="Cases", color="Region",
              title="Yearly Distribution of HFMD Cases per Region")
st.plotly_chart(fig2, use_container_width=True)
st.info("Higher medians & variability in Central/Southern.")
st.markdown("---")

st.header("3) Normalized Regional Pattern (Radar)")
norm_means = df_m[regions].mean()
minv, maxv = norm_means.min(), norm_means.max()
normalized = (norm_means - minv) / (maxv - minv + 1e-9)

fig3 = go.Figure()
vals = normalized.tolist() + [normalized.iloc[0]]
thetas = [r.title() for r in regions] + [regions[0].title()]
fig3.add_trace(go.Scatterpolar(r=vals, theta=thetas, fill='toself', name="HFMD Intensity"))
fig3.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=False,
                   title="Normalized Regional HFMD Intensity")
st.plotly_chart(fig3, use_container_width=True)
st.info("Clear regional imbalance: Central & Southern show strongest normalized levels.")

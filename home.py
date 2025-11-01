import streamlit as st
import plotly.express as px
from data_loader import load_monthly

st.title("🦠 HFMD Malaysia: Temporal & Seasonal Trend (2009–2019)")
st.markdown("---")

df_m = load_monthly()

# Summary box
avg_monthly = df_m["total_cases"].mean()
peak_year = df_m.groupby("Year")["total_cases"].mean().idxmax()
month_means = df_m.groupby("Month")["total_cases"].mean().sort_values(ascending=False)
top_months = month_means.head(3).index.tolist()
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
seasonal_peak = "–".join(month_names[m-1] for m in sorted(top_months))
coverage = f"{df_m['Year'].min()}–{df_m['Year'].max()}"

c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg Monthly Cases", f"{avg_monthly:.0f}", border=True)
c2.metric("Peak Year", f"{int(peak_year)}", border=True)
c3.metric("Seasonal Peak", seasonal_peak, border=True)
c4.metric("Coverage", coverage, border=True)
st.markdown("---")

# Data preview
st.header("1. Data Preview (Monthly)")
st.dataframe(df_m.head(), use_container_width=True)
st.markdown("---")

# Viz 1: line
st.header("2. Monthly HFMD Cases Trend")
fig1 = px.line(df_m, x="Date", y="total_cases",
               title="Monthly Trend of HFMD Cases (2009–2019)",
               labels={"Date":"Year","total_cases":"Avg Monthly Cases"},
               line_shape="spline")
st.plotly_chart(fig1, use_container_width=True)
st.info("Cyclical mid-year peaks indicate strong seasonal trends.")
st.markdown("---")

# Viz 2: yearly bar
st.header("3. Average Yearly HFMD Cases")
yearly = df_m.groupby("Year")["total_cases"].mean().reset_index()
fig2 = px.bar(yearly, x="Year", y="total_cases",
              color="total_cases", color_continuous_scale="Reds",
              title="Average Yearly HFMD Cases (2009–2019)",
              labels={"total_cases":"Avg Monthly Cases"})
st.plotly_chart(fig2, use_container_width=True)
st.info("Certain years show higher baseline incidence.")
st.markdown("---")

# Viz 3: heatmap
st.header("4. Seasonal Pattern (Month × Year)")
pivot = df_m.pivot_table(values="total_cases", index="Month", columns="Year", aggfunc="mean")
fig3 = px.imshow(pivot, aspect="auto", origin="lower",
                 color_continuous_scale="YlOrRd",
                 labels=dict(x="Year", y="Month", color="Avg Monthly Cases"),
                 title="Seasonal Heatmap of HFMD Cases")
fig3.update_yaxes(tickmode="array", tickvals=list(range(1,13)), ticktext=month_names)
st.plotly_chart(fig3, use_container_width=True)
st.info("Recurrent mid-year surges confirmed across years.")

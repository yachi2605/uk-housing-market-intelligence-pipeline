import streamlit as st
import plotly.express as px
import pandas as pd

DATA = st.session_state["DATA"]
filter_by_date = st.session_state["filter_by_date"]
fmt_currency = st.session_state["fmt_currency"]
fmt_pct = st.session_state["fmt_pct"]

st.header("Executive Overview")

kpi = DATA.get("mart_kpi_overall.csv", pd.DataFrame())
monthly = filter_by_date(DATA.get("mart_monthly_kpis.csv", pd.DataFrame()))

# KPI strip
if not kpi.empty:
    row = kpi.iloc[0].to_dict()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Transactions", f"{int(row.get('transactions', 0)):,}")
    c2.metric("Median Price", fmt_currency(row.get("median_price")))
    c3.metric("Total Revenue", fmt_currency(row.get("total_revenue")))
    c4.metric("New-build Share", fmt_pct(row.get("new_build_rate")))
    c5.metric("Freehold Share", fmt_pct(row.get("freehold_rate")))
else:
    st.warning("Missing mart_kpi_overall.csv")

st.markdown("---")

# Trends
if monthly.empty or "month" not in monthly.columns:
    st.error("Missing mart_monthly_kpis.csv or invalid month column.")
    st.stop()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Median Price Trend")
    fig = px.line(monthly.sort_values("month"), x="month", y="median_price")
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sales Volume Trend")
    fig = px.area(monthly.sort_values("month"), x="month", y="sales_volume")
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns([2, 1], gap="large")

with col3:
    st.subheader("Total Revenue Trend")
    fig = px.line(monthly.sort_values("month"), x="month", y="total_revenue")
    fig.update_layout(height=320, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Latest Month Snapshot")
    latest = monthly.sort_values("month").tail(1)
    show_cols = [c for c in ["month","sales_volume","median_price","total_revenue"] if c in latest.columns]
    st.dataframe(latest[show_cols], use_container_width=True, hide_index=True)

# Meaningful insight callout
m = monthly.sort_values("month")
if len(m) >= 2:
    last = m.iloc[-1]
    prev = m.iloc[-2]
    price_change = (last["median_price"] - prev["median_price"]) / prev["median_price"] if prev["median_price"] else None
    vol_change = (last["sales_volume"] - prev["sales_volume"]) / prev["sales_volume"] if prev["sales_volume"] else None
    st.markdown(
        f"""
        <div class="callout">
        <b>Insight (last month vs prior month)</b><br>
        Median price change: <b>{(price_change*100):.2f}%</b> •
        Sales volume change: <b>{(vol_change*100):.2f}%</b><br>
        Use this page to identify whether price movement is supported by activity (volume).
        </div>
        """,
        unsafe_allow_html=True
    )

st.download_button(
    "Download: monthly_kpis.csv (filtered)",
    data=monthly.to_csv(index=False).encode("utf-8"),
    file_name="monthly_kpis_filtered.csv",
    mime="text/csv"
)
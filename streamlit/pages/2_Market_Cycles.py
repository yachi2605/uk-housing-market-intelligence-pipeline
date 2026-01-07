import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

DATA = st.session_state["DATA"]
filter_by_date = st.session_state["filter_by_date"]
fmt_currency = st.session_state["fmt_currency"]
fmt_pct = st.session_state["fmt_pct"]

st.header("Market Cycles & Seasonality")

monthly = filter_by_date(DATA.get("mart_monthly_kpis.csv", pd.DataFrame()))
yoy = filter_by_date(DATA.get("mart_monthly_kpis_yoy.csv", pd.DataFrame()))
index_df = filter_by_date(DATA.get("mart_price_index_monthly.csv", pd.DataFrame()))
season = DATA.get("mart_seasonality_month.csv", pd.DataFrame())

if monthly.empty:
    st.error("Missing mart_monthly_kpis.csv — required for this page.")
    st.stop()

# -------------------------
# Key takeaways (non-technical)
# -------------------------
st.subheader("Key takeaways (what to look for)")

m = monthly.sort_values("month")
latest = m.iloc[-1] if len(m) else None
prev = m.iloc[-2] if len(m) >= 2 else None

price_mom = None
vol_mom = None
if latest is not None and prev is not None and prev.get("median_price", 0) not in (0, None):
    price_mom = (latest["median_price"] - prev["median_price"]) / prev["median_price"]
if latest is not None and prev is not None and prev.get("sales_volume", 0) not in (0, None):
    vol_mom = (latest["sales_volume"] - prev["sales_volume"]) / prev["sales_volume"]

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    st.markdown("**Short-term momentum**")
    if price_mom is None:
        st.write("Not enough data.")
    else:
        st.write(f"Median price moved **{price_mom*100:.2f}%** vs previous month.")

with c2:
    st.markdown("**Activity signal**")
    if vol_mom is None:
        st.write("Not enough data.")
    else:
        st.write(f"Sales volume moved **{vol_mom*100:.2f}%** vs previous month.")

with c3:
    st.markdown("**How to interpret**")
    st.write("Use **YoY** to avoid seasonality. Use **seasonality** to understand normal monthly dips/spikes.")

st.markdown(
    """
    <div class="callout">
    <b>What this page means (plain language)</b><br>
    Some months are naturally busy and others are naturally slow. This page helps you separate:
    <b>(1) seasonal patterns</b> from <b>(2) real market growth/decline</b>.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -------------------------
# Visuals
# -------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("YoY Median Price Growth (best signal)")
    if yoy.empty:
        st.warning("mart_monthly_kpis_yoy.csv missing.")
    else:
        yoy = yoy.sort_values("month")
        fig = px.line(yoy, x="month", y="yoy_median_price")
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Seasonality: Sales Volume by Month-of-Year")
    if season.empty:
        st.warning("mart_seasonality_month.csv missing.")
    else:
        season = season.sort_values("month_of_year")
        fig = px.line(season, x="month_of_year", y="sales_volume")
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Price Index (normalizes long-term trend)")
if index_df.empty:
    st.info("mart_price_index_monthly.csv missing.")
else:
    index_df = index_df.sort_values("month")
    fig = px.line(index_df, x="month", y="median_price_index")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Details (tables) moved to expander
# -------------------------
with st.expander("See data details (for analysts)"):
    if not yoy.empty:
        cols = [c for c in ["month", "yoy_median_price", "yoy_sales_volume", "yoy_total_revenue"] if c in yoy.columns]
        st.dataframe(yoy[cols].tail(24), use_container_width=True, hide_index=True)
        st.download_button(
            "Download YoY table (filtered)",
            data=yoy.to_csv(index=False).encode("utf-8"),
            file_name="monthly_kpis_yoy_filtered.csv",
            mime="text/csv",
        )
import streamlit as st
import pandas as pd

DATA = st.session_state["DATA"]
filter_by_date = st.session_state["filter_by_date"]
fmt_currency = st.session_state["fmt_currency"]
fmt_pct = st.session_state["fmt_pct"]

st.header("Start Here: What this dashboard is and how to use it")

st.markdown(
    """
    <div class="callout">
    <b>What you’re looking at</b><br>
    This dashboard summarizes UK property transaction data into clear decision views:
    <b>market health</b>, <b>price trends</b>, <b>regional differences</b>, <b>product (property type) performance</b>,
    <b>district segments</b>, and a <b>12-month outlook</b>.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ✅ 3-step workflow box (non-technical)
st.subheader("How to use this dashboard (3-step workflow)")

st.markdown(
    """
    <div class="callout">
    <b>Step 1 — Understand the market direction (2 minutes)</b><br>
    Go to <b>Executive Overview</b>. If median price is rising and sales volume is rising, momentum is strong.
    If price rises but volume falls, it may be supply-driven (riskier).<br><br>

    <b>Step 2 — Choose where to focus (3 minutes)</b><br>
    Go to <b>Regional Performance</b> and <b>Concentration (Pareto)</b>. Identify the counties/districts that drive most activity
    and compare price levels vs variability (IQR).<br><br>

    <b>Step 3 — Choose what to build / prioritize (3 minutes)</b><br>
    Go to <b>Product Strategy</b>. Pick property types with high demand (volume) and strong pricing power (premiums).
    Use <b>Segmentation</b> to tailor strategy by district segment. Use <b>Forecasting</b> for planning.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.subheader("How to read key terms (plain language)")
    st.markdown(
        """
        - **Transactions / Sales Volume**: how many properties were sold (activity level).
        - **Median Price**: the “typical” price (less affected by extreme values than average).
        - **Revenue**: total value of transactions (market turnover).
        - **New-build share**: % of sales that are newly built properties.
        - **Freehold vs Leasehold**: UK ownership types; freehold often sells at a premium.
        """
    )

with c2:
    st.subheader("Property type codes (so charts are understandable)")
    st.markdown(
        """
        - **F** = Flat / Maisonette  
        - **S** = Semi-detached  
        - **D** = Detached  
        - **T** = Terraced  
        - **O** = Other / uncategorized (interpret carefully)  
        """
    )

st.markdown("---")

# Auto headlines
monthly = filter_by_date(DATA.get("mart_monthly_kpis.csv", pd.DataFrame()))
county_kpis = DATA.get("mart_county_kpis.csv", pd.DataFrame())
type_kpis = DATA.get("mart_property_type_kpis_extended.csv", pd.DataFrame())

st.subheader("Quick headlines (auto-generated)")

headline_cols = st.columns(3, gap="large")

with headline_cols[0]:
    st.markdown("**Market direction (most recent month)**")
    if monthly.empty or "month" not in monthly.columns:
        st.info("Monthly KPI table not available.")
    else:
        m = monthly.sort_values("month")
        if len(m) < 2:
            st.info("Not enough months to compare.")
        else:
            last = m.iloc[-1]
            prev = m.iloc[-2]
            price_change = (last["median_price"] - prev["median_price"]) / prev["median_price"] if prev["median_price"] else 0
            vol_change = (last["sales_volume"] - prev["sales_volume"]) / prev["sales_volume"] if prev["sales_volume"] else 0
            st.write(f"- Median price: **{fmt_currency(last['median_price'])}**")
            st.write(f"- Price change: **{price_change*100:.2f}%** vs prior month")
            st.write(f"- Activity change: **{vol_change*100:.2f}%** vs prior month")

with headline_cols[1]:
    st.markdown("**Where the market is most active**")
    if county_kpis.empty:
        st.info("County KPI table not available.")
    else:
        top = county_kpis.sort_values("sales_volume", ascending=False).head(1)
        r = top.iloc[0]
        st.write(f"- Top county by sales: **{r['county']}**")
        st.write(f"- Transactions: **{int(r['sales_volume']):,}**")
        if "median_price" in top.columns:
            st.write(f"- Typical price: **{fmt_currency(r['median_price'])}**")

with headline_cols[2]:
    st.markdown("**What people buy most**")
    if type_kpis.empty:
        st.info("Property-type KPI table not available.")
    else:
        top = type_kpis.sort_values("sales_volume", ascending=False).head(1)
        r = top.iloc[0]
        st.write(f"- Most common type: **{r['property_type']}**")
        st.write(f"- Sales volume: **{int(r['sales_volume']):,}**")
        st.write(f"- Typical price: **{fmt_currency(r['median_price'])}**")

st.markdown("---")

st.subheader("If you only have 2 minutes…")
st.markdown(
    """
    - Go to **Executive Overview** to understand overall direction (prices + activity).  
    - Then go to **Regional Performance** to see where the action is (top counties/districts).  
    """
)

st.markdown(
    """
    <div class="callout">
    <b>Note</b><br>
    This dashboard is designed for <b>strategy decisions</b> (focus areas, product mix, timing).
    It does not predict the exact sale price of an individual property.
    </div>
    """,
    unsafe_allow_html=True
)
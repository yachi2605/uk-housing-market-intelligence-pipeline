import streamlit as st
import plotly.express as px
import pandas as pd

DATA = st.session_state["DATA"]
filter_by_date = st.session_state["filter_by_date"]
fmt_currency = st.session_state["fmt_currency"]

st.header("Regional Performance (Where to focus)")

county_kpis = DATA.get("mart_county_kpis.csv", pd.DataFrame())
district_kpis = DATA.get("mart_district_kpis.csv", pd.DataFrame())
disp = DATA.get("mart_county_dispersion.csv", pd.DataFrame())
county_growth = filter_by_date(DATA.get("mart_county_growth_yoy.csv", pd.DataFrame()))

if county_kpis.empty:
    st.error("Missing mart_county_kpis.csv — required for this page.")
    st.stop()

st.markdown(
    """
    <div class="callout">
    <b>What this page means (plain language)</b><br>
    This page helps you decide <b>where to focus</b> by comparing regions on:
    <b>activity (sales volume)</b>, <b>typical price</b>, and <b>price variability (risk)</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# County selector (drill)
counties = sorted(county_kpis["county"].dropna().unique().tolist()) if "county" in county_kpis.columns else []
selected_county = st.selectbox("Pick a county to drill into districts:", counties) if counties else None

# Top 3 takeaways
st.subheader("Key takeaways (quick)")
top_vol = county_kpis.sort_values("sales_volume", ascending=False).head(3)
top_price = county_kpis.sort_values("median_price", ascending=False).head(3) if "median_price" in county_kpis.columns else pd.DataFrame()

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    st.markdown("**Most active counties**")
    for _, r in top_vol.iterrows():
        st.write(f"- {r['county']} (**{int(r['sales_volume']):,}** sales)")

with c2:
    st.markdown("**Highest typical prices**")
    if top_price.empty:
        st.write("Not available.")
    else:
        for _, r in top_price.iterrows():
            st.write(f"- {r['county']} (**{fmt_currency(r['median_price'])}**)")

with c3:
    st.markdown("**How to use this**")
    st.write("Use high-volume counties for liquidity and execution. Use premium counties for margin strategies. Use dispersion to understand risk.")

st.markdown("---")

# Visuals (charts first)
left, right = st.columns(2, gap="large")

with left:
    st.subheader("Top Counties by Sales Volume")
    top25 = county_kpis.sort_values("sales_volume", ascending=False).head(25)
    fig = px.bar(top25, x="county", y="sales_volume")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Risk/Volatility: Dispersion vs Price")
    if disp.empty:
        st.warning("mart_county_dispersion.csv missing.")
    else:
        d = disp.sort_values("n_sales", ascending=False).head(60)
        fig = px.scatter(
            d,
            x="iqr",
            y="median_price",
            size="n_sales",
            hover_name="county",
        )
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

# Drill into districts (chart + then details)
st.subheader("District drilldown (inside selected county)")
if selected_county and not district_kpis.empty and "county" in district_kpis.columns:
    dsub = district_kpis[district_kpis["county"] == selected_county].copy()
    dsub = dsub.sort_values("sales_volume", ascending=False)

    # Chart: top districts by volume
    topd = dsub.head(20)
    fig = px.bar(topd, x="district", y="sales_volume", title=f"Top Districts by Sales Volume — {selected_county}")
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

    # Optional YoY chart for county
    if not county_growth.empty and "county" in county_growth.columns and "yoy_median_price" in county_growth.columns:
        cg = county_growth[county_growth["county"] == selected_county].sort_values("month")
        if not cg.empty:
            fig = px.line(cg, x="month", y="yoy_median_price", title=f"YoY Median Price Growth — {selected_county}")
            fig.add_hline(y=0, line_dash="dash")
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("See district table (details)"):
        show_cols = [c for c in ["district","sales_volume","median_price","total_revenue"] if c in dsub.columns]
        st.dataframe(dsub[show_cols].head(60), use_container_width=True, hide_index=True)
        st.download_button(
            f"Download districts — {selected_county}",
            data=dsub.to_csv(index=False).encode("utf-8"),
            file_name=f"districts_{selected_county}.csv".replace(" ", "_"),
            mime="text/csv",
        )
else:
    st.info("Pick a county to see district drilldown.")
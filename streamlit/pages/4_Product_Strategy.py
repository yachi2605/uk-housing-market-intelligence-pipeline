import streamlit as st
import plotly.express as px
import pandas as pd

DATA = st.session_state["DATA"]
filter_by_date = st.session_state["filter_by_date"]
fmt_currency = st.session_state["fmt_currency"]
fmt_pct = st.session_state["fmt_pct"]

st.header("Product Strategy (Type, New-build, Tenure)")
map_property_type = st.session_state["map_property_type"]

types_ext = DATA.get("mart_property_type_kpis_extended.csv", pd.DataFrame())
types_basic = DATA.get("mart_property_type_kpis.csv", pd.DataFrame())
nb_overall = DATA.get("mart_new_build_premium_overall.csv", pd.DataFrame())
nb_by_type = DATA.get("mart_new_build_premium_by_type.csv", pd.DataFrame())
ten_overall = DATA.get("mart_tenure_effect_overall.csv", pd.DataFrame())
ten_by_type = DATA.get("mart_tenure_effect_by_type.csv", pd.DataFrame())

if types_ext.empty and types_basic.empty:
    st.error("Missing property type KPI tables.")
    st.stop()



# KPI strip (premium cards)
c1, c2, c3, c4 = st.columns(4)

with c1:
    if not nb_overall.empty and "new_build_premium_pct" in nb_overall.columns:
        st.metric("New-build Premium (Overall)", fmt_pct(nb_overall.iloc[0]["new_build_premium_pct"]))
    else:
        st.metric("New-build Premium (Overall)", "—")

with c2:
    if not ten_overall.empty and "freehold_premium_pct" in ten_overall.columns:
        st.metric("Freehold Premium (Overall)", fmt_pct(ten_overall.iloc[0]["freehold_premium_pct"]))
    else:
        st.metric("Freehold Premium (Overall)", "—")

with c3:
    if not nb_overall.empty and "median_new_build" in nb_overall.columns:
        st.metric("Median New-build", fmt_currency(nb_overall.iloc[0]["median_new_build"]))
    else:
        st.metric("Median New-build", "—")

with c4:
    if not nb_overall.empty and "median_existing" in nb_overall.columns:
        st.metric("Median Existing", fmt_currency(nb_overall.iloc[0]["median_existing"]))
    else:
        st.metric("Median Existing", "—")

st.markdown("---")

# Property type performance
st.subheader("Property Type Performance")
df = types_ext if not types_ext.empty else types_basic

if "property_type" in df.columns:
    df = df.sort_values("sales_volume", ascending=False)
    show_cols = [c for c in ["property_type","sales_volume","median_price","avg_price","total_revenue","new_build_rate","freehold_rate","iqr"] if c in df.columns]
    st.dataframe(df[show_cols], use_container_width=True, hide_index=True)

    fig = px.bar(df, x="property_type", y="sales_volume", title="Demand: Sales Volume by Property Type")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    if "median_price" in df.columns:
        fig = px.bar(df, x="property_type", y="median_price", title="Pricing: Median Price by Property Type")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.subheader("New-build Premium by Type")
    if nb_by_type.empty:
        st.warning("mart_new_build_premium_by_type.csv missing.")
    else:
        nb_by_type = nb_by_type.sort_values("new_build_premium_pct", ascending=False)
        st.dataframe(nb_by_type, use_container_width=True, hide_index=True)
        fig = px.bar(nb_by_type, x="property_type", y="new_build_premium_pct")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Freehold Premium by Type")
    if ten_by_type.empty:
        st.warning("mart_tenure_effect_by_type.csv missing.")
    else:
        ten_by_type = ten_by_type.sort_values("freehold_premium_pct", ascending=False)
        st.dataframe(ten_by_type, use_container_width=True, hide_index=True)
        fig = px.bar(ten_by_type, x="property_type", y="freehold_premium_pct")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    <div class="callout">
    <b>How to use this page</b><br>
    Demand = sales volume. Pricing power = median price + premiums. 
    Prioritize property types that combine high demand with strong premiums (new-build and/or freehold).
    </div>
    """,
    unsafe_allow_html=True
)

df = map_property_type(df)
nb_by_type = map_property_type(nb_by_type)
ten_by_type = map_property_type(ten_by_type)
import streamlit as st
import plotly.express as px
import pandas as pd

DATA = st.session_state["DATA"]
fmt_currency = st.session_state["fmt_currency"]
fmt_pct = st.session_state["fmt_pct"]

st.header("Segmentation (Groups of similar districts)")

seg = DATA.get("mart_district_segments.csv", pd.DataFrame())
if seg.empty:
    st.error("Missing mart_district_segments.csv — required for this page.")
    st.stop()

# Make sure numeric columns behave
for c in ["median_price","new_build_rate","freehold_rate","iqr_price","n_sales"]:
    if c in seg.columns:
        seg[c] = pd.to_numeric(seg[c], errors="coerce")

st.markdown(
    """
    <div class="callout">
    <b>What this page means (plain language)</b><br>
    Segmentation groups districts that behave similarly (pricing, new-build share, tenure mix).
    It helps you avoid treating the UK market as “one market” — instead you can tailor strategy by segment.
    </div>
    """,
    unsafe_allow_html=True
)

# Segment selector
segments = sorted(seg["district_segment"].dropna().unique().tolist()) if "district_segment" in seg.columns else []
selected_seg = st.selectbox("View segment:", ["All"] + [str(s) for s in segments], index=0)

view = seg.copy()
if selected_seg != "All":
    view = view[view["district_segment"].astype(str) == selected_seg]

# -------------------------
# Key takeaways
# -------------------------
st.subheader("Key takeaways (simple)")
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown("**Big segments = bigger opportunity**")
    if "district_segment" in seg.columns:
        seg_sizes = seg.groupby("district_segment").size().sort_values(ascending=False)
        top_seg = seg_sizes.index[0]
        st.write(f"- Largest segment: **{top_seg}** ({int(seg_sizes.iloc[0])} districts)")
    else:
        st.write("Segment sizes unavailable.")

with c2:
    st.markdown("**High new-build areas**")
    if "new_build_rate" in seg.columns:
        tmp = seg.groupby("district_segment")["new_build_rate"].mean().sort_values(ascending=False)
        st.write(f"- Highest new-build segment: **{tmp.index[0]}** (~{tmp.iloc[0]*100:.1f}%)")
    else:
        st.write("New-build not available.")

with c3:
    st.markdown("**How to use this**")
    st.write("Use segments to choose a product + pricing approach that fits the district profile, not just the county name.")

st.markdown("---")

# -------------------------
# Visuals first (no table-first)
# -------------------------
left, right = st.columns(2, gap="large")

with left:
    st.subheader("Segment map (pricing vs new-build rate)")
    req = {"median_price","new_build_rate","district_segment"}
    if req.issubset(set(seg.columns)):
        fig = px.scatter(
            view,
            x="median_price",
            y="new_build_rate",
            color="district_segment",
            size="n_sales" if "n_sales" in view.columns else None,
            hover_data=[c for c in ["county","district","freehold_rate","iqr_price"] if c in view.columns],
        )
        fig.update_layout(height=430, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Segmentation columns missing for scatter plot.")

with right:
    st.subheader("Segment profile summary (easy comparison)")
    prof = (
        view.groupby("district_segment")
            .agg(
                districts=("district", "count") if "district" in view.columns else ("county","count"),
                median_price=("median_price", "mean"),
                new_build_rate=("new_build_rate", "mean"),
                freehold_rate=("freehold_rate", "mean") if "freehold_rate" in view.columns else ("new_build_rate", "mean"),
                iqr_price=("iqr_price", "mean") if "iqr_price" in view.columns else ("median_price", "mean"),
            )
            .reset_index()
            .sort_values("districts", ascending=False)
    )
    st.dataframe(prof, use_container_width=True, hide_index=True)

    fig = px.bar(prof, x="district_segment", y="districts", title="How big is each segment?")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    <div class="callout">
    <b>Practical example</b><br>
    If a segment has high median price + low dispersion, it may suit premium positioning.
    If a segment has high new-build share, it may suit developer-led growth strategy.
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Details table hidden behind expander
# -------------------------
with st.expander("See district list (details) + download"):
    show_cols = [c for c in [
        "county","district","district_segment","n_sales","median_price","iqr_price",
        "new_build_rate","freehold_rate","share_flat","share_detached","share_terraced"
    ] if c in view.columns]
    st.dataframe(view[show_cols].sort_values("n_sales", ascending=False).head(300), use_container_width=True, hide_index=True)

    st.download_button(
        "Download this district list (current view)",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="district_segments_view.csv",
        mime="text/csv"
    )
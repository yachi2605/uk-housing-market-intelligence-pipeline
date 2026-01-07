from __future__ import annotations

import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="UK Real Estate Intelligence",
    page_icon="🏠",
    layout="wide",
)

EXPORT_DIR = Path("/Users/yachidarji/Documents/DriveY/Project/UK analysis/streamlit/bi_exports")
STYLE_PATH = Path("/Users/yachidarji/Documents/DriveY/Project/UK analysis/streamlit/assets/style.css")

# ---------- Property Type Mapping ----------
TYPE_MAP = {
    "F": "Flat / Maisonette (F)",
    "S": "Semi-detached (S)",
    "D": "Detached (D)",
    "T": "Terraced (T)",
    "O": "Other (O)",
}

def map_property_type(df: pd.DataFrame, col: str = "property_type") -> pd.DataFrame:
    """
    Replace property type codes with full text labels for non-technical users.
    Works safely even if df is empty or the column is missing.
    """
    if df is None or df.empty or col not in df.columns:
        return df
    out = df.copy()
    out[col] = out[col].astype(str).str.strip().map(lambda x: TYPE_MAP.get(x, x))
    return out

# ---------- Loaders ----------
@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    path = EXPORT_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_all() -> dict[str, pd.DataFrame]:
    names = [
        "mart_kpi_overall.csv",
        "mart_monthly_kpis.csv",
        "mart_monthly_kpis_yoy.csv",
        "mart_yearly_kpis.csv",
        "mart_price_index_monthly.csv",
        "mart_seasonality_month.csv",
        "mart_county_kpis.csv",
        "mart_district_kpis.csv",
        "mart_county_dispersion.csv",
        "mart_sales_concentration_county.csv",
        "mart_sales_concentration_district.csv",
        "mart_property_type_kpis.csv",
        "mart_property_type_kpis_extended.csv",
        "mart_new_build_premium_overall.csv",
        "mart_new_build_premium_by_type.csv",
        "mart_tenure_effect_overall.csv",
        "mart_tenure_effect_by_type.csv",
        "mart_monthly_by_property_type.csv",
        "mart_monthly_by_type_newbuild.csv",
        "mart_monthly_by_type_tenure.csv",
        "mart_district_segments.csv",
        "mart_monthly_by_county.csv",
        "mart_county_growth_yoy.csv",
        "mart_district_growth_yoy.csv",
    ]
    return {n: load_csv(n) for n in names}

# ---------- Styling ----------
def apply_style():
    if STYLE_PATH.exists():
        st.markdown(f"<style>{STYLE_PATH.read_text()}</style>", unsafe_allow_html=True)

def ensure_month(df: pd.DataFrame, col: str = "month") -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df
    out = df.copy()
    out[col] = pd.to_datetime(out[col], errors="coerce")
    return out

def fmt_currency(x) -> str:
    try:
        return f"£{float(x):,.0f}"
    except Exception:
        return "—"

def fmt_pct(x) -> str:
    try:
        return f"{float(x) * 100:.1f}%"
    except Exception:
        return "—"

def sidebar_glossary():
    st.sidebar.markdown("### Definitions (hover)")
    st.sidebar.markdown(
        """
        <div class="glossary-wrap">
          <span class="glossary-item" title="How many properties were sold. Higher volume usually means stronger activity.">Transactions / Sales Volume</span><br>
          <span class="glossary-item" title="The middle sale price. More reliable than average when extreme values exist.">Median Price</span><br>
          <span class="glossary-item" title="Total value of transactions (sum of prices). Shows market turnover.">Total Revenue</span><br>
          <span class="glossary-item" title="Year-over-year % change (this month vs same month last year). Helps reduce seasonality confusion.">YoY Growth</span><br>
          <span class="glossary-item" title="Repeating patterns by month-of-year (e.g., fewer sales in winter).">Seasonality</span><br>
          <span class="glossary-item" title="Price spread between the 75th and 25th percentile. Higher IQR = more variability.">IQR (Dispersion)</span><br>
          <span class="glossary-item" title="Concentration view: how much sales come from the top regions.">Pareto / Concentration</span><br>
          <span class="glossary-item" title="Share of sales that are new builds. Often signals growth/development activity.">New-build Share</span><br>
          <span class="glossary-item" title="UK ownership type. Freehold often carries a premium vs leasehold.">Freehold vs Leasehold</span><br>
          <span class="glossary-item" title="Clusters of districts with similar market behavior. Used for strategy targeting.">Segments</span><br>
          <span class="glossary-item" title="Model-based projection using historical patterns. Not a guarantee.">Forecast</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("### Property Type Codes (hover)")
    st.sidebar.markdown(
        """
        <div class="glossary-wrap">
          <span class="glossary-item" title="Flats/maisonettes, common in dense urban areas.">F = Flat / Maisonette</span><br>
          <span class="glossary-item" title="Semi-detached house (shares one wall).">S = Semi-detached</span><br>
          <span class="glossary-item" title="Detached house (no shared walls).">D = Detached</span><br>
          <span class="glossary-item" title="Terraced house (row housing).">T = Terraced</span><br>
          <span class="glossary-item" title="Other/uncategorized. Interpret carefully.">O = Other</span><br>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- App ----------
apply_style()

st.title("UK Real Estate Intelligence")
st.markdown(
    '<div class="small-note">Coded BI app built on curated mart exports (DuckDB → CSV) with KPIs, trends, regional insights, product strategy, segmentation, and forecasting.</div>',
    unsafe_allow_html=True
)

if not EXPORT_DIR.exists():
    st.error("Missing folder `bi_exports/`. Create it and place your exported CSVs inside.")
    st.stop()

data = load_all()

st.sidebar.header("Global Filters")

monthly_base = ensure_month(data.get("mart_monthly_kpis.csv", pd.DataFrame()))
if monthly_base.empty or "month" not in monthly_base.columns:
    st.sidebar.warning("mart_monthly_kpis.csv missing or invalid. Add it to bi_exports/ to enable date filtering.")
    date_min, date_max = None, None
    date_range = None
else:
    date_min = monthly_base["month"].min()
    date_max = monthly_base["month"].max()
    date_range = st.sidebar.date_input(
        "Date range (Monthly)",
        value=(date_min.date(), date_max.date()),
        min_value=date_min.date(),
        max_value=date_max.date(),
    )

def filter_by_date(df: pd.DataFrame, month_col: str = "month") -> pd.DataFrame:
    if df is None or df.empty or date_range is None or month_col not in df.columns:
        return df
    start, end = date_range
    out = df.copy()
    out[month_col] = pd.to_datetime(out[month_col], errors="coerce")
    return out[(out[month_col] >= pd.to_datetime(start)) & (out[month_col] <= pd.to_datetime(end))]

# Sidebar glossary
sidebar_glossary()

# Store for pages
st.session_state["DATA"] = data
st.session_state["filter_by_date"] = filter_by_date
st.session_state["fmt_currency"] = fmt_currency
st.session_state["fmt_pct"] = fmt_pct
st.session_state["map_property_type"] = map_property_type

st.success("Data loaded. Use the Pages menu (left sidebar) to navigate.")
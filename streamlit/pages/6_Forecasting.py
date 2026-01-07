import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

DATA = st.session_state["DATA"]
filter_by_date = st.session_state["filter_by_date"]
fmt_currency = st.session_state["fmt_currency"]
fmt_pct = st.session_state["fmt_pct"]

st.header("Forecasting (SARIMAX)")

# These come from reports in the earlier plan, but if you exported them into bi_exports you can load similarly.
REPORTS_DIR = Path("reports")

def read_report_csv(name: str) -> pd.DataFrame:
    path = REPORTS_DIR / name
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "month" in df.columns:
        df["month"] = pd.to_datetime(df["month"], errors="coerce")
    return df

monthly_actual = filter_by_date(DATA.get("mart_monthly_kpis.csv", pd.DataFrame()))
f_sales = read_report_csv("forecast_sales_volume.csv")
f_price = read_report_csv("forecast_median_price.csv")
metrics = read_report_csv("forecast_backtest_metrics.csv")

if monthly_actual.empty:
    st.warning("mart_monthly_kpis.csv missing — actual series will not show.")

# Metrics
st.subheader("Backtest Metrics")
if metrics.empty:
    st.info("Missing reports/forecast_backtest_metrics.csv (run Task 9).")
else:
    st.dataframe(metrics, use_container_width=True, hide_index=True)

st.markdown("---")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.subheader("Sales Volume Forecast (Next 12 Months)")
    if f_sales.empty:
        st.info("Missing reports/forecast_sales_volume.csv (run Task 9).")
    else:
        # Plot forecast
        fig = px.line(f_sales.sort_values("month"), x="month", y="forecast_sales_volume")
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(f_sales, use_container_width=True, hide_index=True)

with c2:
    st.subheader("Median Price Forecast (Next 12 Months)")
    if f_price.empty:
        st.info("Missing reports/forecast_median_price.csv (run Task 9).")
    else:
        fig = px.line(f_price.sort_values("month"), x="month", y="forecast_median_price")
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(f_price, use_container_width=True, hide_index=True)

st.markdown("---")

# Optional: Overlay actual + forecast (price)
st.subheader("Actual vs Forecast (Overlay)")
if not monthly_actual.empty and not f_price.empty and "month" in monthly_actual.columns:
    actual = monthly_actual[["month","median_price"]].copy()
    actual["series"] = "Actual"

    forecast = f_price[["month","forecast_median_price"]].copy()
    forecast = forecast.rename(columns={"forecast_median_price":"median_price"})
    forecast["series"] = "Forecast"

    combined = pd.concat([actual, forecast], ignore_index=True)
    fig = px.line(combined.sort_values("month"), x="month", y="median_price", color="series")
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Need both monthly actuals and forecast file to show overlay.")

st.markdown(
    """
    <div class="callout">
    <b>How to use forecasts</b><br>
    Forecasts provide a baseline trajectory and uncertainty bands (if you include them).
    In business terms: treat the forecast as planning guidance, not certainty.
    </div>
    """,
    unsafe_allow_html=True
)


from __future__ import annotations

import os
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from statsmodels.tsa.statespace.sarimax import SARIMAX

load_dotenv()

def db_path() -> str:
    return os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")

def train_test_split_ts(df: pd.DataFrame, test_months: int = 12):
    df = df.sort_values("month").reset_index(drop=True)
    if len(df) <= test_months + 24:
        # need enough history; adjust if dataset is short
        test_months = max(6, min(test_months, len(df)//4))
    train = df.iloc[:-test_months].copy()
    test = df.iloc[-test_months:].copy()
    return train, test

def mape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))

def fit_sarimax(train_series: pd.Series, order=(1,1,1), seasonal_order=(1,1,1,12)):
    model = SARIMAX(
        train_series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    res = model.fit(disp=False)
    return res

def forecast_next(res, steps: int):
    pred = res.get_forecast(steps=steps)
    mean = pred.predicted_mean
    ci = pred.conf_int()
    return mean, ci

def main():
    Path("reports").mkdir(exist_ok=True)

    con = duckdb.connect(db_path())
    monthly = con.execute("""
        SELECT month, sales_volume, median_price
        FROM mart.monthly_kpis
        ORDER BY month;
    """).fetchdf()
    con.close()

    monthly["month"] = pd.to_datetime(monthly["month"])
    monthly = monthly.set_index("month")

    # ---------- A) Forecast sales volume ----------
    vol_df = monthly[["sales_volume"]].dropna().copy()
    train, test = train_test_split_ts(vol_df.reset_index(), test_months=12)
    train = train.set_index("month")
    test = test.set_index("month")

    res_vol = fit_sarimax(train["sales_volume"], order=(1,1,1), seasonal_order=(1,1,1,12))

    # Backtest on test horizon
    pred_test = res_vol.get_forecast(steps=len(test)).predicted_mean
    vol_mae = np.mean(np.abs(test["sales_volume"].values - pred_test.values))
    vol_mape = mape(test["sales_volume"].values, pred_test.values)
    print(f"Sales Volume backtest: MAE={vol_mae:.2f}, MAPE={vol_mape:.4f}")

    # Forecast next 12 months
    mean_vol, ci_vol = forecast_next(res_vol, steps=12)
    out_vol = pd.DataFrame({
        "month": mean_vol.index,
        "forecast_sales_volume": mean_vol.values,
        "lower": ci_vol.iloc[:, 0].values,
        "upper": ci_vol.iloc[:, 1].values
    })
    out_vol.to_csv("reports/forecast_sales_volume.csv", index=False)
    print("Saved: reports/forecast_sales_volume.csv")

    # ---------- B) Forecast median price ----------
    price_df = monthly[["median_price"]].dropna().copy()
    train, test = train_test_split_ts(price_df.reset_index(), test_months=12)
    train = train.set_index("month")
    test = test.set_index("month")

    # Median price is often non-stationary; SARIMAX (1,1,1)(1,1,1,12) works well as a baseline
    res_price = fit_sarimax(train["median_price"], order=(1,1,1), seasonal_order=(1,1,1,12))

    pred_test = res_price.get_forecast(steps=len(test)).predicted_mean
    price_mae = np.mean(np.abs(test["median_price"].values - pred_test.values))
    price_mape = mape(test["median_price"].values, pred_test.values)
    print(f"Median Price backtest: MAE={price_mae:.2f}, MAPE={price_mape:.4f}")

    mean_price, ci_price = forecast_next(res_price, steps=12)
    out_price = pd.DataFrame({
        "month": mean_price.index,
        "forecast_median_price": mean_price.values,
        "lower": ci_price.iloc[:, 0].values,
        "upper": ci_price.iloc[:, 1].values
    })
    out_price.to_csv("reports/forecast_median_price.csv", index=False)
    print("Saved: reports/forecast_median_price.csv")

    # Save backtest metrics summary
    metrics = pd.DataFrame([
        {"series": "sales_volume", "mae": vol_mae, "mape": vol_mape},
        {"series": "median_price", "mae": price_mae, "mape": price_mape},
    ])
    metrics.to_csv("reports/forecast_backtest_metrics.csv", index=False)
    print("Saved: reports/forecast_backtest_metrics.csv")

if __name__ == "__main__":
    main()
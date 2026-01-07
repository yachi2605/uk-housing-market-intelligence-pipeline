from __future__ import annotations
import joblib
import pandas as pd
import numpy as np

def main():
    df = pd.read_parquet("data/processed/model_dataset.parquet")

    y = df["log_price"].astype(float)
    X = df[
        ["year", "month", "quarter",
         "property_type", "is_new_build", "duration", "is_freehold",
         "district", "county"]
    ].copy()

    model = joblib.load("models/hgbr_price_model.joblib")
    y_pred = model.predict(X)

    df2 = df.copy()
    df2["residual"] = y - y_pred  # positive => actual higher than predicted

    by_district = (df2.groupby(["county","district"])
                     .agg(n=("residual","count"), mean_residual=("residual","mean"))
                     .query("n >= 200")  # adjust threshold
                     .sort_values("mean_residual", ascending=False))

    by_district.to_csv("reports/district_residual_ranking.csv")
    print(by_district.head(20).to_string())

if __name__ == "__main__":
    main()
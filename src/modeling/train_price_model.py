from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib

def regression_metrics(y_true, y_pred, label=""):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    print(f"{label} MAE={mae:.4f} RMSE={rmse:.4f} R2={r2:.4f}")
    return {"mae": mae, "rmse": rmse, "r2": r2}

def main():
    df = pd.read_parquet("data/processed/model_dataset.parquet")

    # Target is log_price
    y = df["log_price"].astype(float)

    # Features
    X = df[
        ["year", "month", "quarter",
         "property_type", "is_new_build", "duration", "is_freehold",
         "district", "county"]
    ].copy()

    num_features = ["year", "month", "quarter", "is_new_build", "is_freehold"]
    cat_features = ["property_type", "duration", "district", "county"]

    pre_ridge = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=True), cat_features),
        ],
        remainder="drop"
    )

    pre_gbr = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_features),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_features),
        ],
        remainder="drop"
    )

    # Split (holdout test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 1) Baseline: Ridge (interpretable linear hedonic-ish model)
    ridge = Pipeline(steps=[
        ("pre", pre_ridge),
        ("model", Ridge(alpha=2.0, random_state=42))
    ])

    ridge.fit(X_train, y_train)
    pred_ridge = ridge.predict(X_test)
    regression_metrics(y_test, pred_ridge, label="Ridge(log_price)")

    # 2) ML: Gradient boosting (stronger non-linear model)
    gbr = Pipeline(steps=[
        ("pre", pre_gbr),
        ("model", HistGradientBoostingRegressor(
            max_depth=6,
            learning_rate=0.05,
            max_iter=300,
            random_state=42
        ))
    ])

    gbr.fit(X_train, y_train)
    pred_gbr = gbr.predict(X_test)
    regression_metrics(y_test, pred_gbr, label="HGBR(log_price)")

    Path("models").mkdir(exist_ok=True)
    joblib.dump(ridge, "models/ridge_price_model.joblib")
    joblib.dump(gbr, "models/hgbr_price_model.joblib")
    print("✓ Saved models to /models")

if __name__ == "__main__":
    main()

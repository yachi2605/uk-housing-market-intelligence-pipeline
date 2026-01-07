
from __future__ import annotations
import joblib
import pandas as pd
import numpy as np
import shap
from sklearn.model_selection import train_test_split

def main():
    df = pd.read_parquet("data/processed/model_dataset.parquet")

    y = df["log_price"].astype(float)
    X = df[
        ["year", "month", "quarter",
         "property_type", "is_new_build", "duration", "is_freehold",
         "district", "county"]
    ].copy()

    model = joblib.load("models/hgbr_price_model.joblib")
    pre = model.named_steps["pre"]
    gbr = model.named_steps["model"]

    # transform features (dense matrix) and keep feature names
    X_enc = pre.transform(X)
    feature_names = pre.get_feature_names_out()

    # SHAP on a sample (to keep it fast)
    rng = np.random.default_rng(42)
    idx = rng.choice(X_enc.shape[0], size=min(5000, X_enc.shape[0]), replace=False)
    X_sample = X_enc[idx]

    explainer = shap.Explainer(gbr.predict, X_sample, feature_names=feature_names)
    shap_values = explainer(X_sample)

    # Save summary as a CSV: mean absolute SHAP value per feature
    mean_abs = np.abs(shap_values.values).mean(axis=0)
    shap_rank = (pd.DataFrame({"feature": feature_names, "mean_abs_shap": mean_abs})
                   .sort_values("mean_abs_shap", ascending=False))
    shap_rank.to_csv("reports/shap_feature_importance.csv", index=False)
    print(shap_rank.head(30).to_string(index=False))

if __name__ == "__main__":
    main()
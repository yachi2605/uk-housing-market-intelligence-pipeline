from __future__ import annotations
import joblib
import pandas as pd
import numpy as np

def main():
    model = joblib.load("models/ridge_price_model.joblib")
    pre = model.named_steps["pre"]
    ridge = model.named_steps["model"]

    feature_names = pre.get_feature_names_out()
    coefs = ridge.coef_

    out = (pd.DataFrame({"feature": feature_names, "coef": coefs})
             .assign(abs_coef=lambda d: d["coef"].abs())
             .sort_values("abs_coef", ascending=False))

    out.to_csv("reports/ridge_feature_importance.csv", index=False)
    print(out.head(30).to_string(index=False))

if __name__ == "__main__":
    main()
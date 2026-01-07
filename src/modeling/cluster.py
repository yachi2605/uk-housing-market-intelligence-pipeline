from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def main():
    df = pd.read_parquet("data/processed/model_dataset.parquet")

    # Use a sample if dataset is huge (keeps it fast). Increase later.
    if len(df) > 500000:
        df = df.sample(500000, random_state=42).copy()

    X = df[[
        "log_price",
        "property_type",
        "is_new_build",
        "duration",
        "is_freehold",
        "county"
    ]].copy()

    num_features = ["log_price", "is_new_build", "is_freehold"]
    cat_features = ["property_type", "duration", "county"]

    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
        ],
        remainder="drop"
    )

    # Choose K using silhouette on a small subset
    X_small = X.sample(min(50000, len(X)), random_state=42)
    X_small_enc = pre.fit_transform(X_small)

    best_k, best_score = None, -1
    for k in [4, 5, 6, 7, 8, 10]:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_small_enc)
        score = silhouette_score(X_small_enc, labels)
        print(f"k={k} silhouette={score:.4f}")
        if score > best_score:
            best_k, best_score = k, score

    print(f"\n✓ Best k={best_k} (silhouette={best_score:.4f})")

    # Fit final model on full sample
    X_enc = pre.fit_transform(X)
    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    clusters = km_final.fit_predict(X_enc)

    out = df.copy()
    out["segment_id"] = clusters

    Path("reports").mkdir(exist_ok=True)

    # Segment profiles
    prof = (
        out.groupby("segment_id")
           .agg(
               n=("segment_id", "count"),
               median_price=("price", "median"),
               mean_price=("price", "mean"),
               new_build_rate=("is_new_build", "mean"),
               freehold_rate=("is_freehold", "mean")
           )
           .sort_values("n", ascending=False)
    )
    prof.to_csv("reports/segment_profiles.csv")
    print("\nSaved: reports/segment_profiles.csv")
    print(prof.head(20))

    # Save a small labeled sample for dashboard inspection
    sample_out = out.sample(min(20000, len(out)), random_state=42)
    sample_out[[
        "date_of_transfer","price","property_type","is_new_build","duration",
        "district","county","segment_id"
    ]].to_parquet("data/processed/transaction_segment_sample.parquet", index=False)
    print("Saved: data/processed/transaction_segment_sample.parquet")

if __name__ == "__main__":
    main()
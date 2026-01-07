from __future__ import annotations
import os
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

load_dotenv()

def db_path() -> str:
    return os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")

def main():
    con = duckdb.connect(db_path())

    # Ensure features table exists
    con.execute(Path("sql/ddl/007_district_features_duckdb.sql").read_text(encoding="utf-8"))

    df = con.execute("SELECT * FROM mart.district_features;").fetchdf()
    con.close()

    # Features for clustering (exclude identifiers)
    id_cols = ["county", "district"]
    X = df.drop(columns=id_cols).copy()

    # Scale
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # Select K
    best_k, best_score = None, -1
    for k in [3, 4, 5, 6, 7, 8]:
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(Xs)
        score = silhouette_score(Xs, labels)
        print(f"k={k} silhouette={score:.4f}")
        if score > best_score:
            best_k, best_score = k, score

    print(f"\n✓ Best district k={best_k} (silhouette={best_score:.4f})")

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=20)
    df["district_segment"] = km_final.fit_predict(Xs)

    Path("reports").mkdir(exist_ok=True)
    df.to_csv("reports/district_segments.csv", index=False)
    print("Saved: reports/district_segments.csv")

    # Segment profiles (district-level)
    prof = (df.groupby("district_segment")
              .agg(
                  n_districts=("district", "count"),
                  avg_median_price=("median_price","mean"),
                  avg_new_build_rate=("new_build_rate","mean"),
                  avg_freehold_rate=("freehold_rate","mean"),
                  avg_iqr_price=("iqr_price","mean"),
                  avg_share_flat=("share_flat","mean"),
                  avg_share_detached=("share_detached","mean"),
              )
              .sort_values("n_districts", ascending=False))
    prof.to_csv("reports/district_segment_profiles.csv")
    print("\nSaved: reports/district_segment_profiles.csv")
    print(prof)

    # (Optional) write back to DuckDB for dashboard
    con = duckdb.connect(db_path())
    con.execute("CREATE SCHEMA IF NOT EXISTS mart;")
    con.register("df_seg", df)
    con.execute("DROP TABLE IF EXISTS mart.district_segments;")
    con.execute("CREATE TABLE mart.district_segments AS SELECT * FROM df_seg;")
    con.close()
    print("✓ Wrote mart.district_segments into DuckDB")

if __name__ == "__main__":
    main()
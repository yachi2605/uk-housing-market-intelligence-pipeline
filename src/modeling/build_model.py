from __future__ import annotations
import os
from pathlib import Path
import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def db_path() -> str:
    return os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")

def main():
    out_path = Path("data/processed/model_dataset.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(db_path())

    # Keep only “usable” rows for modeling
    df = con.execute("""
        SELECT
          price,
          LOG(price) AS log_price,
          date_of_transfer,
          year,
          month,
          quarter,
          property_type,
          is_new_build,
          duration,
          is_freehold,
          district,
          county
        FROM stg.ppd_clean_valid
        WHERE price IS NOT NULL AND price > 0
          AND year IS NOT NULL
          AND district IS NOT NULL AND district <> ''
          AND county IS NOT NULL AND county <> ''
          AND property_type IN ('F','S','D','T','O');
    """).fetchdf()

    con.close()

    # Basic type casting
    cat_cols = ["property_type", "duration", "district", "county"]
    for c in cat_cols:
        df[c] = df[c].astype("category")

    df.to_parquet(out_path, index=False)
    print(f"✓ Saved modeling dataset: {out_path} with {len(df):,} rows")

if __name__ == "__main__":
    main()
from __future__ import annotations

import os
from pathlib import Path
import duckdb
from dotenv import load_dotenv

load_dotenv()

def duckdb_path() -> str:
    return os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")

def main():
    csv_path = Path("data/raw/kaggle_ppd/price_paid_records.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}. Run `make download` first.")

    print("Using CSV:", csv_path)
    print("DuckDB file:", duckdb_path())

    Path(duckdb_path()).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(duckdb_path())

    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("DROP TABLE IF EXISTS raw.ppd;")

    # Create raw table directly from the header-based CSV
    con.execute(f"""
        CREATE TABLE raw.ppd AS
        SELECT
          "Transaction unique identifier"::VARCHAR               AS transaction_id,
          "Price"::BIGINT                                       AS price,
          "Date of Transfer"::DATE                              AS date_of_transfer,
          "Property Type"::VARCHAR                              AS property_type,
          "Old/New"::VARCHAR                                    AS old_new,
          "Duration"::VARCHAR                                   AS duration,
          "Town/City"::VARCHAR                                  AS town_city,
          "District"::VARCHAR                                   AS district,
          "County"::VARCHAR                                     AS county,
          "PPDCategory Type"::VARCHAR                            AS ppd_category_type,
          "Record Status - monthly file only"::VARCHAR           AS record_status
        FROM read_csv_auto('{csv_path.as_posix()}', header=true, sample_size=200000);
    """)

    con.execute("ANALYZE raw.ppd;")
    n = con.execute("SELECT COUNT(*) FROM raw.ppd;").fetchone()[0]
    print(f"✓ raw.ppd rows: {n:,}")

    print("Tables now in DB:", con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type='BASE TABLE'
        ORDER BY 1,2;
    """).fetchall())

    con.close()

if __name__ == "__main__":
    main()
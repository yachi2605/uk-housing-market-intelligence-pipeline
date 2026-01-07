from __future__ import annotations
import os
from pathlib import Path
import duckdb
from dotenv import load_dotenv

load_dotenv()

def db_path() -> str:
    return os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")

def run_sql(con: duckdb.DuckDBPyConnection, path: Path) -> None:
    con.execute(path.read_text(encoding="utf-8"))

def main():
    con = duckdb.connect(db_path())
    run_sql(con, Path("sql/ddl/005_regional_analysis_duckdb.sql"))

    print("\n--- Top 10 counties by sales volume ---")
    print(con.execute("""
        SELECT county, n_sales, median_price, iqr
        FROM mart.county_dispersion
        ORDER BY n_sales DESC
        LIMIT 10;
    """).fetchdf().to_string(index=False))

    print("\n--- Top 10 counties by median price ---")
    print(con.execute("""
        SELECT county, n_sales, median_price, p90
        FROM mart.county_dispersion
        WHERE n_sales >= 100
        ORDER BY median_price DESC
        LIMIT 10;
    """).fetchdf().to_string(index=False))

    print("\n--- Concentration: counties needed for 80% of sales ---")
    print(con.execute("""
        SELECT MIN(rnk) AS counties_to_reach_80pct
        FROM mart.sales_concentration_county
        WHERE cum_share >= 0.80;
    """).fetchdf().to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
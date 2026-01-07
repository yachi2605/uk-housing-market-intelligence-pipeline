from __future__ import annotations
import os
from pathlib import Path
import duckdb
from dotenv import load_dotenv

load_dotenv()

def db_path() -> str:
    return os.getenv("DUCKDB_PATH", "/Users/yachidarji/Documents/DriveY/Project/UK analysis/data/uk_ppd.duckdb")

def run_sql(con: duckdb.DuckDBPyConnection, path: Path) -> None:
    con.execute(path.read_text(encoding="utf-8"))

def main():
    con = duckdb.connect(db_path())
    run_sql(con, Path("/Users/yachidarji/Documents/DriveY/Project/UK analysis/sql/ddl/004_temporal_analysis_duckdb.sql"))

    print("\n--- Monthly KPIs (last 12) ---")
    print(con.execute("""
        SELECT * FROM mart.monthly_kpis
        ORDER BY month DESC
        LIMIT 12;
    """).fetchdf().to_string(index=False))

    print("\n--- YoY Growth (last 12) ---")
    print(con.execute("""
        SELECT month, yoy_sales_volume, yoy_total_revenue, yoy_median_price
        FROM mart.monthly_kpis_yoy
        ORDER BY month DESC
        LIMIT 12;
    """).fetchdf().to_string(index=False))

    print("\n--- Seasonality by month-of-year ---")
    print(con.execute("""
        SELECT * FROM mart.seasonality_month
        ORDER BY month_of_year;
    """).fetchdf().to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
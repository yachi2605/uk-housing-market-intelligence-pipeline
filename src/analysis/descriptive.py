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

    run_sql(con, Path('/Users/yachidarji/Documents/DriveY/Project/UK analysis/sql/ddl/003_create_marts.sql'))

    print("\n--- Overall KPI ---")
    print(con.execute("SELECT * FROM mart.kpi_overall;").fetchdf().to_string(index=False))

    print("\n--- Property type KPIs (top 10) ---")
    print(con.execute("""
        SELECT * FROM mart.property_type_kpis
        ORDER BY sales_volume DESC
        LIMIT 10;
    """).fetchdf().to_string(index=False))

    print("\n--- Counties (top 10 by volume) ---")
    print(con.execute("""
        SELECT * FROM mart.county_kpis
        ORDER BY sales_volume DESC
        LIMIT 10;
    """).fetchdf().to_string(index=False))

    print("\n--- Monthly KPIs (first 12 rows) ---")
    print(con.execute("""
        SELECT * FROM mart.monthly_kpis
        ORDER BY month
        LIMIT 12;
    """).fetchdf().to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
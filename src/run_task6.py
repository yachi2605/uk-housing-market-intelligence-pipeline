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
    run_sql(con, Path("sql/ddl/006_property_type_performance_duckdb.sql"))

    print("\n--- Property Type KPIs (extended) ---")
    print(con.execute("""
        SELECT property_type, sales_volume, median_price, new_build_rate, freehold_rate
        FROM mart.property_type_kpis_extended
        ORDER BY sales_volume DESC;
    """).fetchdf().to_string(index=False))

    print("\n--- New-build premium overall ---")
    print(con.execute("SELECT * FROM mart.new_build_premium_overall;").fetchdf().to_string(index=False))

    print("\n--- New-build premium by type ---")
    print(con.execute("""
        SELECT property_type, new_build_premium_pct, n_new_build, n_existing
        FROM mart.new_build_premium_by_type
        ORDER BY new_build_premium_pct DESC;
    """).fetchdf().to_string(index=False))

    print("\n--- Tenure effect overall (freehold premium) ---")
    print(con.execute("SELECT * FROM mart.tenure_effect_overall;").fetchdf().to_string(index=False))

    print("\n--- Tenure effect by type ---")
    print(con.execute("""
        SELECT property_type, freehold_premium_pct, n_freehold, n_leasehold
        FROM mart.tenure_effect_by_type
        ORDER BY freehold_premium_pct DESC;
    """).fetchdf().to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
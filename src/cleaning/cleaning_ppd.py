from __future__ import annotations
import os
from pathlib import Path
import duckdb
from dotenv import load_dotenv

load_dotenv()

def db_path() -> str:
    return os.getenv("DUCKDB_PATH", "/Users/yachidarji/Documents/DriveY/Project/UK analysis/data/uk_ppd.duckdb")

def run_sql_file(con: duckdb.DuckDBPyConnection, path: Path) -> None:
    sql_text = path.read_text(encoding="utf-8")
    con.execute(sql_text)

def main():
    con = duckdb.connect(db_path())

    run_sql_file(con, Path("/Users/yachidarji/Documents/DriveY/Project/UK analysis/sql/ddl/002_create_staging_tables.sql"))
    run_sql_file(con, Path("/Users/yachidarji/Documents/DriveY/Project/UK analysis/sql/ddl/002b_quality_report_duckdb.sql"))

    report = con.execute("SELECT * FROM stg.ppd_quality_report;").fetchdf()
    print(report.to_string(index=False))

    # quick sanity peek
    top_types = con.execute("""
        SELECT property_type, COUNT(*) AS n
        FROM stg.ppd_clean_valid
        GROUP BY 1
        ORDER BY n DESC;
    """).fetchall()
    print("\nValid rows by property_type:", top_types)

    con.close()

if __name__ == "__main__":
    main()

    
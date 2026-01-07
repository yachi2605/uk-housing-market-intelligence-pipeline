from __future__ import annotations

import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

def main():
    db_path = os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")
    print("DB:", db_path)

    con = duckdb.connect(db_path)

    # Show schemas + tables (so we can see what's actually there)
    schemas = con.execute("SELECT schema_name FROM information_schema.schemata ORDER BY 1;").fetchall()
    print("Schemas:", [s[0] for s in schemas])

    tables = con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type='BASE TABLE'
        ORDER BY table_schema, table_name;
    """).fetchall()
    print("Tables:", tables)

    # Now validate raw.ppd
    exists = con.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema='raw' AND table_name='ppd';
    """).fetchone()[0] == 1

    if not exists:
        raise SystemExit(
            "raw.ppd not found. Run `make load` first, or your loader wrote to a different DB file.\n"
            "Check DB path above and the Tables list printed above."
        )

    n = con.execute("SELECT COUNT(*) FROM raw.ppd;").fetchone()[0]
    print("row_count:", f"{n:,}")

    top_types = con.execute("""
        SELECT property_type, COUNT(*) AS n
        FROM raw.ppd
        GROUP BY 1
        ORDER BY n DESC
        LIMIT 10;
    """).fetchall()
    print("top property types:", top_types)

    con.close()

if __name__ == "__main__":
    main()
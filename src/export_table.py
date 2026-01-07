import duckdb
import os
from pathlib import Path

DB = os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb")
OUT = Path("bi_exports")
OUT.mkdir(exist_ok=True)

TABLES = [
    "mart.kpi_overall",
    "mart.monthly_kpis",
    "mart.yearly_kpis",
    "mart.property_type_kpis",
    "mart.county_kpis",
    "mart.district_kpis",

    "mart.monthly_kpis_yoy",
    "mart.seasonality_month",
    "mart.price_index_monthly",
    "mart.monthly_by_property_type",
    "mart.monthly_by_county",

    "mart.county_dispersion",
    "mart.sales_concentration_county",
    "mart.sales_concentration_district",
    "mart.county_growth_yoy",
    "mart.district_growth_yoy",

    "mart.property_type_kpis_extended",
    "mart.new_build_premium_overall",
    "mart.new_build_premium_by_type",
    "mart.tenure_effect_overall",
    "mart.tenure_effect_by_type",
    "mart.monthly_by_type_newbuild",
    "mart.monthly_by_type_tenure",

    "mart.district_segments",
]

con = duckdb.connect(DB)

for t in TABLES:
    try:
        df = con.execute(f"SELECT * FROM {t}").fetchdf()
        out = OUT / f"{t.replace('.', '_')}.csv"
        df.to_csv(out, index=False)
        print(f"✓ Exported {out}")
    except Exception as e:
        print(f"⚠️ Skipped {t}: {e}")

con.close()
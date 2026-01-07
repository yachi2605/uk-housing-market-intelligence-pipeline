import duckdb, os, pandas as pd
import matplotlib.pyplot as plt

con = duckdb.connect(os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb"))

monthly = con.execute("SELECT * FROM mart.monthly_kpis ORDER BY month").fetchdf()
types = con.execute("SELECT * FROM mart.property_type_kpis ORDER BY sales_volume DESC").fetchdf()

plt.figure()
plt.plot(monthly["month"], monthly["median_price"])
plt.title("Median Price Over Time (Monthly)")
plt.xlabel("Month")
plt.ylabel("Median price")
plt.tight_layout()
plt.show()

plt.figure()
plt.bar(types["property_type"].astype(str), types["sales_volume"])
plt.title("Sales Volume by Property Type")
plt.xlabel("Property Type (F/S/D/T/O)")
plt.ylabel("Sales volume")
plt.tight_layout()
plt.show()
import duckdb, os
import matplotlib.pyplot as plt

con = duckdb.connect(os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb"))

monthly = con.execute("SELECT * FROM mart.monthly_kpis ORDER BY month").fetchdf()
yoy = con.execute("SELECT * FROM mart.monthly_kpis_yoy ORDER BY month").fetchdf()
season = con.execute("SELECT * FROM mart.seasonality_month ORDER BY month_of_year").fetchdf()

plt.figure()
plt.plot(monthly["month"], monthly["sales_volume"])
plt.title("Sales Volume Over Time (Monthly)")
plt.xlabel("Month"); plt.ylabel("Sales volume")
plt.tight_layout(); plt.show()

plt.figure()
plt.plot(monthly["month"], monthly["median_price"])
plt.title("Median Price Over Time (Monthly)")
plt.xlabel("Month"); plt.ylabel("Median price")
plt.tight_layout(); plt.show()

plt.figure()
plt.plot(yoy["month"], yoy["yoy_median_price"])
plt.title("YoY Median Price Growth")
plt.xlabel("Month"); plt.ylabel("YoY growth (fraction)")
plt.tight_layout(); plt.show()

plt.figure()
plt.plot(season["month_of_year"], season["sales_volume"])
plt.title("Seasonality: Avg Sales Volume by Month-of-Year")
plt.xlabel("Month of year"); plt.ylabel("Avg sales volume")
plt.tight_layout(); plt.show()
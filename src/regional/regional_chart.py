import duckdb, os
import matplotlib.pyplot as plt
import numpy as np

con = duckdb.connect(os.getenv("DUCKDB_PATH", "data/uk_ppd.duckdb"))
pareto = con.execute("""
    SELECT rnk, county, sales, cum_share
    FROM mart.sales_concentration_county
    ORDER BY rnk
    LIMIT 30;
""").fetchdf()

x = np.arange(len(pareto))
plt.figure()
plt.bar(x, pareto["sales"])
plt.xticks(x, pareto["county"], rotation=45, ha="right")
plt.ylabel("Sales volume")
plt.title("County Sales Concentration (Top 30)")
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(x, pareto["cum_share"])
plt.xticks(x, pareto["county"], rotation=45, ha="right")
plt.ylabel("Cumulative share")
plt.title("Pareto Cumulative Share (Top 30 Counties)")
plt.tight_layout()
plt.show()
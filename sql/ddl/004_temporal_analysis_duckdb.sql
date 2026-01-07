CREATE SCHEMA IF NOT EXISTS mart;

-- 1) Monthly KPIs (recreate to ensure consistent)
DROP TABLE IF EXISTS mart.monthly_kpis;
CREATE TABLE mart.monthly_kpis AS
SELECT
  DATE_TRUNC('month', date_of_transfer) AS month,
  COUNT(*)                               AS sales_volume,
  SUM(price)                             AS total_revenue,
  AVG(price)                             AS avg_price,
  MEDIAN(price)                          AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY 1;

-- 2) YoY growth (volume, revenue, median price)
DROP TABLE IF EXISTS mart.monthly_kpis_yoy;
CREATE TABLE mart.monthly_kpis_yoy AS
WITH base AS (
  SELECT
    month,
    sales_volume,
    total_revenue,
    median_price,
    LAG(sales_volume, 12)  OVER (ORDER BY month) AS sales_volume_prev_year,
    LAG(total_revenue, 12) OVER (ORDER BY month) AS total_revenue_prev_year,
    LAG(median_price, 12)  OVER (ORDER BY month) AS median_price_prev_year
  FROM mart.monthly_kpis
)
SELECT
  month,
  sales_volume,
  total_revenue,
  median_price,
  sales_volume_prev_year,
  total_revenue_prev_year,
  median_price_prev_year,

  CASE WHEN sales_volume_prev_year IS NULL OR sales_volume_prev_year = 0 THEN NULL
       ELSE (sales_volume - sales_volume_prev_year) * 1.0 / sales_volume_prev_year END AS yoy_sales_volume,

  CASE WHEN total_revenue_prev_year IS NULL OR total_revenue_prev_year = 0 THEN NULL
       ELSE (total_revenue - total_revenue_prev_year) * 1.0 / total_revenue_prev_year END AS yoy_total_revenue,

  CASE WHEN median_price_prev_year IS NULL OR median_price_prev_year = 0 THEN NULL
       ELSE (median_price - median_price_prev_year) * 1.0 / median_price_prev_year END AS yoy_median_price
FROM base
ORDER BY month;

-- 3) Monthly by property type (supports stacked/lines by type)
DROP TABLE IF EXISTS mart.monthly_by_property_type;
CREATE TABLE mart.monthly_by_property_type AS
SELECT
  DATE_TRUNC('month', date_of_transfer) AS month,
  property_type,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  MEDIAN(price) AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1,2
ORDER BY 1,2;

-- 4) Monthly by county (top regions trend)
DROP TABLE IF EXISTS mart.monthly_by_county;
CREATE TABLE mart.monthly_by_county AS
SELECT
  DATE_TRUNC('month', date_of_transfer) AS month,
  county,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  MEDIAN(price) AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1,2
ORDER BY 1,2;

-- 5) Seasonality: average by month-of-year across all years
DROP TABLE IF EXISTS mart.seasonality_month;
CREATE TABLE mart.seasonality_month AS
SELECT
  EXTRACT(month FROM date_of_transfer) AS month_of_year,
  AVG(price)    AS avg_price,
  MEDIAN(price) AS median_price,
  COUNT(*)      AS sales_volume
FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY 1;

-- 6) Simple monthly price index (base=100 at first month)
DROP TABLE IF EXISTS mart.price_index_monthly;
CREATE TABLE mart.price_index_monthly AS
WITH base AS (
  SELECT month, median_price
  FROM mart.monthly_kpis
  ORDER BY month
),
first_val AS (
  SELECT median_price AS base_median
  FROM base
  ORDER BY month
  LIMIT 1
)
SELECT
  b.month,
  b.median_price,
  (b.median_price * 100.0 / f.base_median) AS median_price_index
FROM base b
CROSS JOIN first_val f
ORDER BY b.month;
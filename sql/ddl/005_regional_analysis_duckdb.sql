CREATE SCHEMA IF NOT EXISTS mart;

-- Helper: monthly county metrics (base for growth)
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

-- Helper: monthly district metrics (base for growth)
DROP TABLE IF EXISTS mart.monthly_by_district;
CREATE TABLE mart.monthly_by_district AS
SELECT
  DATE_TRUNC('month', date_of_transfer) AS month,
  district,
  county,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  MEDIAN(price) AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1,2,3
ORDER BY 1,2,3;

-- 1) County YoY growth (volume + median price)
DROP TABLE IF EXISTS mart.county_growth_yoy;
CREATE TABLE mart.county_growth_yoy AS
WITH base AS (
  SELECT
    month,
    county,
    sales_volume,
    median_price,
    LAG(sales_volume, 12) OVER (PARTITION BY county ORDER BY month) AS vol_prev_year,
    LAG(median_price, 12) OVER (PARTITION BY county ORDER BY month) AS med_prev_year
  FROM mart.monthly_by_county
)
SELECT
  month,
  county,
  sales_volume,
  median_price,
  vol_prev_year,
  med_prev_year,
  CASE WHEN vol_prev_year IS NULL OR vol_prev_year = 0 THEN NULL
       ELSE (sales_volume - vol_prev_year) * 1.0 / vol_prev_year END AS yoy_sales_volume,
  CASE WHEN med_prev_year IS NULL OR med_prev_year = 0 THEN NULL
       ELSE (median_price - med_prev_year) * 1.0 / med_prev_year END AS yoy_median_price
FROM base
ORDER BY month, county;

-- 2) District YoY growth (volume + median price)
DROP TABLE IF EXISTS mart.district_growth_yoy;
CREATE TABLE mart.district_growth_yoy AS
WITH base AS (
  SELECT
    month,
    district,
    county,
    sales_volume,
    median_price,
    LAG(sales_volume, 12) OVER (PARTITION BY district ORDER BY month) AS vol_prev_year,
    LAG(median_price, 12) OVER (PARTITION BY district ORDER BY month) AS med_prev_year
  FROM mart.monthly_by_district
)
SELECT
  month,
  district,
  county,
  sales_volume,
  median_price,
  vol_prev_year,
  med_prev_year,
  CASE WHEN vol_prev_year IS NULL OR vol_prev_year = 0 THEN NULL
       ELSE (sales_volume - vol_prev_year) * 1.0 / vol_prev_year END AS yoy_sales_volume,
  CASE WHEN med_prev_year IS NULL OR med_prev_year = 0 THEN NULL
       ELSE (median_price - med_prev_year) * 1.0 / med_prev_year END AS yoy_median_price
FROM base
ORDER BY month, district;

-- 3) County dispersion (how spread out prices are within each county)
-- Uses IQR and P90/P10 as robust dispersion measures.
DROP TABLE IF EXISTS mart.county_dispersion;
CREATE TABLE mart.county_dispersion AS
SELECT
  county,
  COUNT(*) AS n_sales,
  AVG(price) AS avg_price,
  MEDIAN(price) AS median_price,
  QUANTILE_CONT(price, 0.10) AS p10,
  QUANTILE_CONT(price, 0.25) AS p25,
  QUANTILE_CONT(price, 0.75) AS p75,
  QUANTILE_CONT(price, 0.90) AS p90,
  (QUANTILE_CONT(price, 0.75) - QUANTILE_CONT(price, 0.25)) AS iqr,
  (QUANTILE_CONT(price, 0.90) - QUANTILE_CONT(price, 0.10)) AS p90_p10_spread
FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY n_sales DESC;

-- 4) Sales concentration (Pareto) by county
DROP TABLE IF EXISTS mart.sales_concentration_county;
CREATE TABLE mart.sales_concentration_county AS
WITH counts AS (
  SELECT county, COUNT(*) AS sales
  FROM stg.ppd_clean_valid
  GROUP BY 1
),
ranked AS (
  SELECT
    county,
    sales,
    ROW_NUMBER() OVER (ORDER BY sales DESC) AS rnk,
    SUM(sales) OVER () AS total_sales,
    SUM(sales) OVER (ORDER BY sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_sales
  FROM counts
)
SELECT
  county,
  sales,
  rnk,
  sales * 1.0 / total_sales AS share,
  cum_sales * 1.0 / total_sales AS cum_share
FROM ranked
ORDER BY rnk;

-- 5) Sales concentration (Pareto) by district
DROP TABLE IF EXISTS mart.sales_concentration_district;
CREATE TABLE mart.sales_concentration_district AS
WITH counts AS (
  SELECT district, county, COUNT(*) AS sales
  FROM stg.ppd_clean_valid
  GROUP BY 1,2
),
ranked AS (
  SELECT
    district,
    county,
    sales,
    ROW_NUMBER() OVER (ORDER BY sales DESC) AS rnk,
    SUM(sales) OVER () AS total_sales,
    SUM(sales) OVER (ORDER BY sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_sales
  FROM counts
)
SELECT
  district,
  county,
  sales,
  rnk,
  sales * 1.0 / total_sales AS share,
  cum_sales * 1.0 / total_sales AS cum_share
FROM ranked
ORDER BY rnk;
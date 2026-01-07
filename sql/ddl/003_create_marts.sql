CREATE SCHEMA IF NOT EXISTS mart;

-- 1) Overall KPI summary
DROP TABLE IF EXISTS mart.kpi_overall;
CREATE TABLE mart.kpi_overall AS
SELECT
  COUNT(*)                         AS transactions,
  COUNT(DISTINCT district)         AS districts,
  COUNT(DISTINCT county)           AS counties,
  MIN(date_of_transfer)            AS min_date,
  MAX(date_of_transfer)            AS max_date,
  AVG(price)                       AS avg_price,
  MEDIAN(price)                    AS median_price,
  QUANTILE_CONT(price, 0.25)       AS p25_price,
  QUANTILE_CONT(price, 0.75)       AS p75_price,
  SUM(price)                       AS total_revenue,
  AVG(is_new_build)                AS new_build_rate,
  AVG(is_freehold)                 AS freehold_rate
FROM stg.ppd_clean_valid;

-- 2) Monthly market KPIs (for time-series + dashboard)
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

-- 3) Yearly KPIs
DROP TABLE IF EXISTS mart.yearly_kpis;
CREATE TABLE mart.yearly_kpis AS
SELECT
  year,
  COUNT(*)       AS sales_volume,
  SUM(price)     AS total_revenue,
  AVG(price)     AS avg_price,
  MEDIAN(price)  AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY 1;

-- 4) Property type overview
DROP TABLE IF EXISTS mart.property_type_kpis;
CREATE TABLE mart.property_type_kpis AS
SELECT
  property_type,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  AVG(price)    AS avg_price,
  MEDIAN(price) AS median_price,
  AVG(is_new_build) AS new_build_rate,
  AVG(is_freehold)  AS freehold_rate
FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY sales_volume DESC;

-- 5) County overview
DROP TABLE IF EXISTS mart.county_kpis;
CREATE TABLE mart.county_kpis AS
SELECT
  county,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  AVG(price)    AS avg_price,
  MEDIAN(price) AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY sales_volume DESC;

-- 6) District overview (often the most useful)
DROP TABLE IF EXISTS mart.district_kpis;
CREATE TABLE mart.district_kpis AS
SELECT
  district,
  county,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  AVG(price)    AS avg_price,
  MEDIAN(price) AS median_price
FROM stg.ppd_clean_valid
GROUP BY 1, 2
ORDER BY sales_volume DESC;
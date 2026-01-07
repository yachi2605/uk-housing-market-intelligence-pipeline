CREATE SCHEMA IF NOT EXISTS mart;

-- 1) Extended property type KPIs (including splits)
DROP TABLE IF EXISTS mart.property_type_kpis_extended;
CREATE TABLE mart.property_type_kpis_extended AS
SELECT
  property_type,
  COUNT(*)      AS sales_volume,
  SUM(price)    AS total_revenue,
  AVG(price)    AS avg_price,
  MEDIAN(price) AS median_price,

  -- shares
  AVG(is_new_build) AS new_build_rate,
  AVG(is_freehold)  AS freehold_rate,

  -- dispersion
  QUANTILE_CONT(price, 0.25) AS p25,
  QUANTILE_CONT(price, 0.75) AS p75,
  (QUANTILE_CONT(price, 0.75) - QUANTILE_CONT(price, 0.25)) AS iqr

FROM stg.ppd_clean_valid
GROUP BY 1
ORDER BY sales_volume DESC;

-- 2) New-build premium overall (median-based, robust)
DROP TABLE IF EXISTS mart.new_build_premium_overall;
CREATE TABLE mart.new_build_premium_overall AS
WITH med AS (
  SELECT
    is_new_build,
    MEDIAN(price) AS median_price,
    COUNT(*) AS n
  FROM stg.ppd_clean_valid
  GROUP BY 1
)
SELECT
  (SELECT median_price FROM med WHERE is_new_build=1) AS median_new_build,
  (SELECT median_price FROM med WHERE is_new_build=0) AS median_existing,
  (SELECT n FROM med WHERE is_new_build=1) AS n_new_build,
  (SELECT n FROM med WHERE is_new_build=0) AS n_existing,
  CASE
    WHEN (SELECT median_price FROM med WHERE is_new_build=0) IS NULL
      OR (SELECT median_price FROM med WHERE is_new_build=0) = 0
    THEN NULL
    ELSE
      ((SELECT median_price FROM med WHERE is_new_build=1) -
       (SELECT median_price FROM med WHERE is_new_build=0)) * 1.0
       / (SELECT median_price FROM med WHERE is_new_build=0)
  END AS new_build_premium_pct;

-- 3) New-build premium by property type
DROP TABLE IF EXISTS mart.new_build_premium_by_type;
CREATE TABLE mart.new_build_premium_by_type AS
WITH med AS (
  SELECT
    property_type,
    is_new_build,
    MEDIAN(price) AS median_price,
    COUNT(*) AS n
  FROM stg.ppd_clean_valid
  GROUP BY 1,2
)
SELECT
  property_type,
  MAX(CASE WHEN is_new_build=1 THEN median_price END) AS median_new_build,
  MAX(CASE WHEN is_new_build=0 THEN median_price END) AS median_existing,
  MAX(CASE WHEN is_new_build=1 THEN n END) AS n_new_build,
  MAX(CASE WHEN is_new_build=0 THEN n END) AS n_existing,
  CASE
    WHEN MAX(CASE WHEN is_new_build=0 THEN median_price END) IS NULL
      OR MAX(CASE WHEN is_new_build=0 THEN median_price END) = 0
      OR MAX(CASE WHEN is_new_build=1 THEN median_price END) IS NULL
    THEN NULL
    ELSE
      (MAX(CASE WHEN is_new_build=1 THEN median_price END) -
       MAX(CASE WHEN is_new_build=0 THEN median_price END)) * 1.0
      / MAX(CASE WHEN is_new_build=0 THEN median_price END)
  END AS new_build_premium_pct
FROM med
GROUP BY 1
ORDER BY new_build_premium_pct DESC;

-- 4) Tenure effect overall (freehold vs leasehold median diff)
DROP TABLE IF EXISTS mart.tenure_effect_overall;
CREATE TABLE mart.tenure_effect_overall AS
WITH med AS (
  SELECT
    is_freehold,
    MEDIAN(price) AS median_price,
    COUNT(*) AS n
  FROM stg.ppd_clean_valid
  WHERE duration IN ('F','L')  -- keep only known tenure
  GROUP BY 1
)
SELECT
  (SELECT median_price FROM med WHERE is_freehold=1) AS median_freehold,
  (SELECT median_price FROM med WHERE is_freehold=0) AS median_leasehold,
  (SELECT n FROM med WHERE is_freehold=1) AS n_freehold,
  (SELECT n FROM med WHERE is_freehold=0) AS n_leasehold,
  CASE
    WHEN (SELECT median_price FROM med WHERE is_freehold=0) IS NULL
      OR (SELECT median_price FROM med WHERE is_freehold=0) = 0
    THEN NULL
    ELSE
      ((SELECT median_price FROM med WHERE is_freehold=1) -
       (SELECT median_price FROM med WHERE is_freehold=0)) * 1.0
       / (SELECT median_price FROM med WHERE is_freehold=0)
  END AS freehold_premium_pct;

-- 5) Tenure effect by property type
DROP TABLE IF EXISTS mart.tenure_effect_by_type;
CREATE TABLE mart.tenure_effect_by_type AS
WITH med AS (
  SELECT
    property_type,
    is_freehold,
    MEDIAN(price) AS median_price,
    COUNT(*) AS n
  FROM stg.ppd_clean_valid
  WHERE duration IN ('F','L')
  GROUP BY 1,2
)
SELECT
  property_type,
  MAX(CASE WHEN is_freehold=1 THEN median_price END) AS median_freehold,
  MAX(CASE WHEN is_freehold=0 THEN median_price END) AS median_leasehold,
  MAX(CASE WHEN is_freehold=1 THEN n END) AS n_freehold,
  MAX(CASE WHEN is_freehold=0 THEN n END) AS n_leasehold,
  CASE
    WHEN MAX(CASE WHEN is_freehold=0 THEN median_price END) IS NULL
      OR MAX(CASE WHEN is_freehold=0 THEN median_price END) = 0
      OR MAX(CASE WHEN is_freehold=1 THEN median_price END) IS NULL
    THEN NULL
    ELSE
      (MAX(CASE WHEN is_freehold=1 THEN median_price END) -
       MAX(CASE WHEN is_freehold=0 THEN median_price END)) * 1.0
      / MAX(CASE WHEN is_freehold=0 THEN median_price END)
  END AS freehold_premium_pct
FROM med
GROUP BY 1
ORDER BY freehold_premium_pct DESC;

-- 6) Monthly trends by property type AND new-build flag
DROP TABLE IF EXISTS mart.monthly_by_type_newbuild;
CREATE TABLE mart.monthly_by_type_newbuild AS
SELECT
  DATE_TRUNC('month', date_of_transfer) AS month,
  property_type,
  is_new_build,
  COUNT(*)      AS sales_volume,
  MEDIAN(price) AS median_price,
  SUM(price)    AS total_revenue
FROM stg.ppd_clean_valid
GROUP BY 1,2,3
ORDER BY 1,2,3;

-- 7) Monthly trends by property type AND tenure (F/L only)
DROP TABLE IF EXISTS mart.monthly_by_type_tenure;
CREATE TABLE mart.monthly_by_type_tenure AS
SELECT
  DATE_TRUNC('month', date_of_transfer) AS month,
  property_type,
  duration,
  COUNT(*)      AS sales_volume,
  MEDIAN(price) AS median_price,
  SUM(price)    AS total_revenue
FROM stg.ppd_clean_valid
WHERE duration IN ('F','L')
GROUP BY 1,2,3
ORDER BY 1,2,3;
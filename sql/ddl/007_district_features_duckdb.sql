CREATE SCHEMA IF NOT EXISTS mart;

DROP TABLE IF EXISTS mart.district_features;

CREATE TABLE mart.district_features AS
SELECT
  county,
  district,
  COUNT(*) AS n_sales,
  MEDIAN(price) AS median_price,
  AVG(price) AS avg_price,
  QUANTILE_CONT(price, 0.75) - QUANTILE_CONT(price, 0.25) AS iqr_price,
  AVG(is_new_build) AS new_build_rate,
  AVG(is_freehold) AS freehold_rate,

  -- property type mix
  AVG(CASE WHEN property_type='F' THEN 1 ELSE 0 END) AS share_flat,
  AVG(CASE WHEN property_type='S' THEN 1 ELSE 0 END) AS share_semi,
  AVG(CASE WHEN property_type='D' THEN 1 ELSE 0 END) AS share_detached,
  AVG(CASE WHEN property_type='T' THEN 1 ELSE 0 END) AS share_terraced,
  AVG(CASE WHEN property_type='O' THEN 1 ELSE 0 END) AS share_other

FROM stg.ppd_clean_valid
GROUP BY 1,2
HAVING COUNT(*) >= 500;  -- keep only districts with enough data
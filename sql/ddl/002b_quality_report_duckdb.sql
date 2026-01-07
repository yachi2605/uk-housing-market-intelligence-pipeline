CREATE SCHEMA IF NOT EXISTS stg;

DROP TABLE IF EXISTS stg.ppd_quality_report;

CREATE TABLE stg.ppd_quality_report AS
SELECT
  (SELECT COUNT(*) FROM raw.ppd) AS raw_rows,
  (SELECT COUNT(*) FROM stg.ppd_clean) AS staged_rows,
  (SELECT COUNT(*) FROM stg.ppd_clean_valid) AS valid_rows,

  (SELECT COUNT(*) FROM stg.ppd_clean WHERE price IS NULL OR price <= 0) AS bad_price_rows,
  (SELECT COUNT(*) FROM stg.ppd_clean WHERE date_of_transfer IS NULL) AS missing_date_rows,
  (SELECT COUNT(*) FROM stg.ppd_clean WHERE district IS NULL OR district = '') AS missing_district_rows,

  (SELECT COUNT(*) FROM stg.ppd_clean WHERE property_type NOT IN ('F','S','D','T','O') OR property_type IS NULL) AS invalid_property_type_rows,
  (SELECT COUNT(*) FROM stg.ppd_clean WHERE old_new NOT IN ('Y','N') OR old_new IS NULL) AS invalid_old_new_rows,
  (SELECT COUNT(*) FROM stg.ppd_clean WHERE duration NOT IN ('F','L') OR duration IS NULL) AS invalid_duration_rows;
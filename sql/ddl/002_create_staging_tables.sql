CREATE SCHEMA IF NOT EXISTS stg;

DROP TABLE IF EXISTS stg.ppd_clean;

-- Clean + standardize
CREATE TABLE stg.ppd_clean AS
SELECT
  -- IDs
  TRIM(transaction_id) AS transaction_id,

  -- price (remove invalids later)
  price::BIGINT AS price,

  -- date
  date_of_transfer::DATE AS date_of_transfer,

  -- normalize categorical fields
  UPPER(TRIM(property_type)) AS property_type,   -- F/S/D/T/O
  UPPER(TRIM(old_new))       AS old_new,         -- Y/N
  UPPER(TRIM(duration))      AS duration,        -- F/L (freehold/leasehold) sometimes U
  UPPER(TRIM(town_city))     AS town_city,
  UPPER(TRIM(district))      AS district,
  UPPER(TRIM(county))        AS county,
  UPPER(TRIM(ppd_category_type)) AS ppd_category_type,
  UPPER(TRIM(record_status))     AS record_status,

  -- engineered time features
  EXTRACT(year FROM date_of_transfer)    AS year,
  EXTRACT(month FROM date_of_transfer)   AS month,
  EXTRACT(quarter FROM date_of_transfer) AS quarter,

  -- engineered binary flags
  CASE WHEN UPPER(TRIM(old_new)) = 'Y' THEN 1 ELSE 0 END AS is_new_build,
  CASE WHEN UPPER(TRIM(duration)) = 'F' THEN 1 ELSE 0 END AS is_freehold

FROM raw.ppd;

-- Remove obvious bad rows (create a cleaned view/table)
-- If you prefer not to drop rows, we can instead add a "is_valid" flag. For now we filter.
DROP TABLE IF EXISTS stg.ppd_clean_valid;

CREATE TABLE stg.ppd_clean_valid AS
SELECT *
FROM stg.ppd_clean
WHERE
  price IS NOT NULL AND price > 0
  AND date_of_transfer IS NOT NULL
  AND district IS NOT NULL AND district <> ''
  AND property_type IN ('F','S','D','T','O');  -- Flat, Semi, Detached, Terraced, Other

CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.ppd;
CREATE TABLE raw.ppd (
  transaction_id     text,
  price              bigint,
  date_of_transfer   date,
  property_type      text,
  old_new            text,
  duration           text,
  town_city          text,
  district           text,
  county             text,
  ppd_category_type  text,
  record_status      text
);

CREATE INDEX IF NOT EXISTS idx_ppd_date     ON raw.ppd(date_of_transfer);
CREATE INDEX IF NOT EXISTS idx_ppd_district ON raw.ppd(district);
CREATE INDEX IF NOT EXISTS idx_ppd_town     ON raw.ppd(town_city);
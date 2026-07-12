-- Clean and standardize raw sensor readings into a staging view.
-- Adds simple date parts and flags anything that looks out of spec.

CREATE OR REPLACE VIEW stg_sensor_data AS
SELECT
    container_id,
    timestamp,
    CAST(timestamp AS DATE)              AS reading_date,
    EXTRACT(HOUR FROM timestamp)          AS reading_hour,
    temperature,
    humidity,
    co2_level,
    CASE
        WHEN temperature > 4.5 OR co2_level > 620 THEN TRUE
        ELSE FALSE
    END AS is_anomalous
FROM raw_sensor_data;
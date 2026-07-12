-- Aggregate staging data per container to see which ones are
-- drifting enough to count as a spoilage arbitrage opportunity.

CREATE OR REPLACE TABLE mart_spoilage_arbitrage AS
SELECT
    container_id,
    COUNT(*)                                            AS total_readings,
    SUM(CASE WHEN is_anomalous THEN 1 ELSE 0 END)        AS anomalous_readings,
    ROUND(
        100.0 * SUM(CASE WHEN is_anomalous THEN 1 ELSE 0 END) / COUNT(*),
        2
    )                                                    AS anomaly_pct,
    (100.0 * SUM(CASE WHEN is_anomalous THEN 1 ELSE 0 END) / COUNT(*)) > 5.0
                                                          AS arbitrage_flag
FROM stg_sensor_data
GROUP BY container_id
ORDER BY anomaly_pct DESC;
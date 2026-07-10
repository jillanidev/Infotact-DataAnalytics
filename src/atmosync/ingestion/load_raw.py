# Validates mock sensor data against the schema, then loads whatever
# passes into the DuckDB raw zone. Bad rows get logged and dropped
# instead of silently going in.

from typing import List

import duckdb
import pandas as pd
from pydantic import ValidationError

from atmosync.utils.config import jillani_config
from atmosync.utils.logger import jillani_get_logger
from atmosync.schemas.sensor import SensorReading
from atmosync.ingestion.mock_sensor import jillani_generate_mock_readings

jillani_logger = jillani_get_logger(__name__)

JILLANI_RAW_TABLE_NAME = "raw_sensor_data"


def jillani_validate_readings(df: pd.DataFrame) -> pd.DataFrame:
    """Check each row against SensorReading. Drop and log anything that fails."""
    valid_rows: List[dict] = []
    error_count = 0

    for record in df.to_dict(orient="records"):
        try:
            reading = SensorReading(**record)
            valid_rows.append(reading.model_dump())
        except ValidationError as exc:
            error_count += 1
            jillani_logger.warning(f"Dropped invalid reading for {record.get('container_id')}: {exc}")

    if error_count:
        jillani_logger.warning(f"{error_count} rows failed validation and were dropped")

    jillani_logger.info(f"{len(valid_rows)} rows passed validation")
    return pd.DataFrame(valid_rows)


def jillani_ensure_raw_table(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the raw_sensor_data table if it doesn't exist yet."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {JILLANI_RAW_TABLE_NAME} (
            container_id VARCHAR,
            timestamp TIMESTAMP,
            temperature DOUBLE,
            humidity DOUBLE,
            co2_level DOUBLE
        )
        """
    )


def jillani_load_raw_sensor_data(df: pd.DataFrame) -> int:
    """Validate and insert a DataFrame of readings into DuckDB. Returns rows inserted."""
    jillani_config.db_path.parent.mkdir(parents=True, exist_ok=True)

    validated_df = jillani_validate_readings(df)
    if validated_df.empty:
        jillani_logger.warning("No valid rows to load — skipping insert")
        return 0

    conn = duckdb.connect(database=str(jillani_config.db_path))
    try:
        jillani_ensure_raw_table(conn)
        conn.register("jillani_validated_view", validated_df)
        conn.execute(f"INSERT INTO {JILLANI_RAW_TABLE_NAME} SELECT * FROM jillani_validated_view")
        row_count = conn.execute(f"SELECT COUNT(*) FROM {JILLANI_RAW_TABLE_NAME}").fetchone()[0]
        jillani_logger.info(f"Inserted {len(validated_df)} rows. Table now has {row_count} total rows.")
        return len(validated_df)
    finally:
        conn.close()


if __name__ == "__main__":
    mock_df = jillani_generate_mock_readings(num_rows=1000)
    jillani_load_raw_sensor_data(mock_df)
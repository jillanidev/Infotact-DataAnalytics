# Generates mock IoT sensor readings for the container fleet.
# Stands in for the real hardware feed while we build the pipeline.

from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

from atmosync.utils.logger import jillani_get_logger

jillani_logger = jillani_get_logger(__name__)

# Fleet + baseline ranges, meant to look like a real cold-chain
# container carrying produce rather than pure random noise.
JILLANI_CONTAINER_IDS = [f"CTR-{i:03d}" for i in range(1, 13)]
JILLANI_BASE_TEMP_C = 4.0
JILLANI_BASE_HUMIDITY_PCT = 55.0
JILLANI_BASE_CO2_PPM = 600.0


def jillani_generate_mock_readings(num_rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate `num_rows` of mock sensor telemetry as a DataFrame."""
    rng = np.random.default_rng(seed)

    container_ids = rng.choice(JILLANI_CONTAINER_IDS, size=num_rows)

    # Spread timestamps over the last `num_rows` minutes, oldest first,
    # so it reads like a real time series once loaded.
    now = datetime.now(timezone.utc)
    timestamps = [now - timedelta(minutes=int(m)) for m in range(num_rows, 0, -1)]

    # A small fraction of containers drift out of spec — this is the
    # exact signal the Spoilage Arbitrage model will key off of later.
    drift_mask = rng.random(num_rows) < 0.05
    drift_amount = np.where(drift_mask, rng.uniform(2.0, 6.0, size=num_rows), 0.0)

    temperature = JILLANI_BASE_TEMP_C + rng.normal(0, 0.5, size=num_rows) + drift_amount
    humidity = JILLANI_BASE_HUMIDITY_PCT + rng.normal(0, 3.0, size=num_rows) + (drift_amount * 2)
    co2_level = JILLANI_BASE_CO2_PPM + rng.normal(0, 50.0, size=num_rows) + (drift_amount * 30)

    mock_df = pd.DataFrame({
        "container_id": container_ids,
        "timestamp": timestamps,
        "temperature": np.round(temperature, 2),
        "humidity": np.round(humidity, 2),
        "co2_level": np.round(co2_level, 2),
    })

    jillani_logger.info(f"Generated {len(mock_df)} mock sensor rows ({drift_mask.sum()} drifting)")
    return mock_df


if __name__ == "__main__":
    df = jillani_generate_mock_readings()
    print(df.head())
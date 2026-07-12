# Connects to the warehouse and runs the SQL transformation scripts
# in order: staging view first, then the spoilage mart table.

from pathlib import Path

import duckdb

from atmosync.utils.config import jillani_config
from atmosync.utils.logger import jillani_get_logger

jillani_logger = jillani_get_logger(__name__)

# sql/ lives at the project root, three levels up from this file
# (src/atmosync/transform/run_transformations.py -> project root).
JILLANI_PROJECT_ROOT = Path(__file__).resolve().parents[3]
JILLANI_SQL_DIR = JILLANI_PROJECT_ROOT / "sql"

JILLANI_TRANSFORM_SCRIPTS = [
    "01_clean_sensors.sql",
    "02_spoilage_mart.sql",
]


def jillani_read_sql_file(filename: str) -> str:
    sql_path = JILLANI_SQL_DIR / filename
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    return sql_path.read_text()


def jillani_run_transformations() -> None:
    conn = duckdb.connect(database=str(jillani_config.db_path))
    try:
        for script_name in JILLANI_TRANSFORM_SCRIPTS:
            jillani_logger.info(f"Running {script_name}")
            sql_text = jillani_read_sql_file(script_name)
            conn.execute(sql_text)
            jillani_logger.info(f"Finished {script_name}")

        row_count = conn.execute("SELECT COUNT(*) FROM mart_spoilage_arbitrage").fetchone()[0]
        jillani_logger.info(f"mart_spoilage_arbitrage now has {row_count} containers")
    finally:
        conn.close()


if __name__ == "__main__":
    jillani_run_transformations()
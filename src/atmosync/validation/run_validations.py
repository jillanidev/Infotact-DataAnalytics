"""
AtmoSync Data Quality (DQ) validation module.

Runs a couple of basic sanity checks against mart_spoilage_arbitrage
after the pipeline runs. If either check fails, we exit non-zero so
the orchestrator (or CI) can tell the run wasn't clean.
"""

import logging
import sys
from pathlib import Path

import duckdb

# --- Logging setup -------------------------------------------------------

logger = logging.getLogger("AtmoSync-DQ")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- Paths -----------------------------------------------------------------

# This file lives at src/atmosync/validation/run_validations.py, so the
# project root is three levels up. Points at the same DuckDB file every
# other step in the pipeline reads and writes.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "marts" / "atmosync.duckdb"

MART_TABLE = "mart_spoilage_arbitrage"


def check_table_not_empty(conn: duckdb.DuckDBPyConnection) -> bool:
    """Test 1 (Completeness): the mart table should have at least one row."""
    row_count = conn.execute(f"SELECT COUNT(*) FROM {MART_TABLE}").fetchone()[0]

    if row_count > 0:
        logger.info(f"[PASS] Completeness check: {row_count} rows in {MART_TABLE}")
        return True

    logger.error(f"[FAIL] Completeness check: {MART_TABLE} has 0 rows")
    return False


def check_no_null_container_ids(conn: duckdb.DuckDBPyConnection) -> bool:
    """Test 2 (Integrity): container_id should never be NULL."""
    null_count = conn.execute(
        f"SELECT COUNT(*) FROM {MART_TABLE} WHERE container_id IS NULL"
    ).fetchone()[0]

    if null_count == 0:
        logger.info("[PASS] Integrity check: no NULL container_id values")
        return True

    logger.error(f"[FAIL] Integrity check: {null_count} NULL container_id values found")
    return False


def run_validations() -> None:
    """Run all DQ checks against the DuckDB warehouse. Exit 1 if any fail."""
    logger.info("=== AtmoSync data quality checks started ===")

    if not DB_PATH.exists():
        logger.error(f"Database file not found at {DB_PATH}")
        sys.exit(1)

    conn = duckdb.connect(database=str(DB_PATH))
    try:
        results = [
            check_table_not_empty(conn),
            check_no_null_container_ids(conn),
        ]
    finally:
        conn.close()

    if all(results):
        logger.info("=== All data quality checks passed ===")
    else:
        logger.error("=== One or more data quality checks failed ===")
        sys.exit(1)


if __name__ == "__main__":
    run_validations()
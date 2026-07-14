"""
AtmoSync Pipeline Orchestrator.

Runs the ingestion step and the transformation step, in order, as
separate subprocesses. If a step fails, the pipeline stops right
there -- we never want the mart built on top of a bad ingestion run.
"""

import logging
import subprocess
import sys
from pathlib import Path

# --- Logging setup -------------------------------------------------------

logger = logging.getLogger("AtmoSync-Orchestrator")
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

# This file lives at src/atmosync/orchestration/pipeline.py, so the
# project root is three levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"

VALIDATION_SCRIPT = SRC_DIR / "atmosync" / "validation" / "run_validations.py"
TRANSFORM_SCRIPT = SRC_DIR / "atmosync" / "transform" / "run_transformations.py"


def run_step(step_name: str, script_path: Path) -> None:
    """
    Run a single pipeline step in its own subprocess.

    Both scripts live inside the atmosync package and use package-relative
    imports (e.g. `from atmosync.utils.config import jillani_config`), so
    we invoke them with `python -m <module.path>` from the src/ directory.
    That's functionally the same as running the script directly, just
    done in a way that lets Python resolve the package imports correctly.
    """
    module_path = (
        script_path.relative_to(SRC_DIR)
        .with_suffix("")
        .as_posix()
        .replace("/", ".")
    )

    logger.info(f"Starting step: {step_name} ({module_path})")

    try:
        subprocess.run(
            [sys.executable, "-m", module_path],
            cwd=str(SRC_DIR),
            check=True,
        )
        logger.info(f"Completed step: {step_name}")

    except subprocess.CalledProcessError as exc:
        logger.error(
            f"Step '{step_name}' failed with exit code {exc.returncode}. "
            f"Stopping pipeline."
        )
        sys.exit(1)

    except Exception as exc:
        logger.error(f"Unexpected error while running '{step_name}': {exc}")
        sys.exit(1)


def run_pipeline() -> None:
    """Run the full AtmoSync pipeline: ingestion, then transformation."""
    logger.info("=== AtmoSync pipeline run started ===")

    run_step("Ingestion", INGESTION_SCRIPT)
    run_step("Transformation", TRANSFORM_SCRIPT)
    run_step("Validation", VALIDATION_SCRIPT)
    logger.info("=== AtmoSync pipeline run finished successfully ===")


if __name__ == "__main__":
    run_pipeline()
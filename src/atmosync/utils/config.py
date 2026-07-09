import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class JillaniAtmoSyncConfig(BaseModel):
    db_path: Path = Path(os.getenv("ATMOSYNC_DB_PATH", "data/marts/atmosync.duckdb"))
    log_level: str = os.getenv("ATMOSYNC_LOG_LEVEL", "INFO")
    raw_data_dir: Path = Path("data/raw")
    staging_data_dir: Path = Path("data/staging")
    
    class Config:
        arbitrary_types_allowed = True

jillani_config = JillaniAtmoSyncConfig()
import os
from pathlib import Path
from functools import lru_cache

class Settings():
    def __init__(self):
        self.project_dir = Path(os.getenv("PROJECT_DIR", "/beegfs/sets/aw-ciroh/projects/LE_lstm_eval"))
        self.scripts_dir = Path(os.getenv("SCRIPTS_DIR", "/beegfs/sets/aw-ciroh/projects/LE_lstm_eval/scripts"))

@lru_cache
def get_settings() -> Settings:
    return Settings()
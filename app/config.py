import os
from pathlib import Path
from functools import lru_cache

class Settings():
    def __init__(self):
        self.project_dir = Path(os.getenv("PROJECT_DIR", "/beegfs/sets/aw-ciroh/projects/LE_lstm_eval"))
        self.scripts_dir = Path(os.getenv("SCRIPTS_DIR", "/beegfs/sets/aw-ciroh/projects/LE_lstm_eval/scripts"))
        self.wendian_host = Path(os.getenv("WENDIAN_HOST", "wendian.mines.edu"))
        self.wendian_user = Path(os.getenv("WENDIAN_USER", "lagonafer"))
        self.wendian_password = Path(os.getenv("WENDIAN_PASSWORD"))

@lru_cache
def get_settings() -> Settings:
    return Settings()
import json
import os
from typing import Optional

from . import util

def get_config_file_path() -> str:
    """Returns the path to the config file."""
    return os.path.join(util.get_app_data_dir(), "config.json")

def save_download_directory(path: str) -> None:
    """Saves the download directory to the config file."""
    assert isinstance(path, str) and path, "path must be a non-empty string"
    config = {"download_directory": path}
    with open(get_config_file_path(), "w") as f:
        json.dump(config, f)

def load_download_directory() -> Optional[str]:
    """Loads the download directory from the config file."""
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            assert isinstance(config, dict), "config must be a dictionary"
            return config.get("download_directory")
    return None

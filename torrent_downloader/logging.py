import logging
import sys
import os
from typing import Optional

from . import util

_CONFIGURED = False
_LOG_FILE: Optional[str] = None

DEFAULT_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def setup_logging(level: int = logging.DEBUG) -> str:
    """Configure root logging handlers (file + stderr) if not already done.

    Parameters
    ----------
    level: int
        Root logger level (defaults to DEBUG for maximum diagnostics).

    Returns
    -------
    str
        Path to the log file used.
    """
    assert isinstance(level, int), "level must be an integer"
    global _CONFIGURED, _LOG_FILE
    if _CONFIGURED and _LOG_FILE is not None:
        return _LOG_FILE

    log_dir = util.get_log_dir()
    # Ensure directory exists before creating FileHandler
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'torrentdownloader.log')

    # ``force=True`` ensures a clean slate (Py3.8+) without accumulating handlers
    logging.basicConfig(
        level=level,
        format=DEFAULT_FORMAT,
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stderr),
        ],
        force=True,
    )

    logging.info("Logging initialised")
    logging.debug(f"Platform: {sys.platform}")
    logging.debug(f"Python executable: {sys.executable}")
    logging.debug(f"Python version: {sys.version}")
    logging.debug(f"Current working directory: {os.getcwd()}")
    logging.debug(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    logging.debug(f"App data directory: {util.get_app_data_dir()}")
    logging.debug(f"Log directory: {log_dir}")
    logging.debug(f"Cache directory: {util.get_cache_dir()}")

    _CONFIGURED = True
    _LOG_FILE = log_path
    return log_path

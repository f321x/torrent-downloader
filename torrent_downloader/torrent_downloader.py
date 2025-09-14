import sys
import os
import logging
import traceback
import tkinter as tk

from . import util
from .logging import setup_logging
from .gui import TorrentDownloaderApp


# Create necessary directories
app_data_dir = util.get_app_data_dir()
log_dir = util.get_log_dir()
cache_dir = util.get_cache_dir()

for directory in [app_data_dir, log_dir, cache_dir]:
    os.makedirs(directory, exist_ok=True)


def main():
    try:
        # Ensure logging configured (idempotent if already done by caller/tests)
        log_file = setup_logging()
        logging.info("Starting TorrentDownloader application")
        logging.debug(f"Log file: {log_file}")
        # Reduced verbose startup logging to essential info
        logging.debug(f"Working directory: {os.getcwd()}")
        logging.debug(f"Executable: {sys.executable}")

        root = tk.Tk()
        # Disable system menu bar on macOS
        if sys.platform == 'darwin':
            logging.info("Configuring macOS-specific settings")
            root.createcommand('::tk::mac::ShowPreferences', lambda: None)
            root.createcommand('::tk::mac::ReopenApplication', lambda: None)
            root.createcommand('::tk::mac::ShowHelp', lambda: None)
            root.createcommand('::tk::mac::Quit', lambda: None)

        app = TorrentDownloaderApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        logging.error(traceback.format_exc())
        print(f"Error starting application: {e}")
        sys.exit(1)



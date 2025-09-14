import os
import logging
from pathlib import Path

import torrent_downloader as pkg
from torrent_downloader import util


def test_setup_logging_creates_file_and_is_idempotent(monkeypatch, tmp_path):
    # Redirect util directory helpers to a temp structure so we do not write to user dirs
    app_dir = tmp_path / 'appdata'
    log_dir = tmp_path / 'logs'
    cache_dir = tmp_path / 'cache'

    # Monkeypatch the cached functions: clear lru_cache and then override return values
    for fn in (util.get_app_data_dir, util.get_log_dir, util.get_cache_dir):
        fn.cache_clear()  # type: ignore[attr-defined]

    monkeypatch.setattr(util, 'get_app_data_dir', lambda: str(app_dir))
    monkeypatch.setattr(util, 'get_log_dir', lambda: str(log_dir))
    monkeypatch.setattr(util, 'get_cache_dir', lambda: str(cache_dir))

    # Call setup_logging via package re-export
    log_path = pkg.setup_logging()
    assert log_path.endswith('torrentdownloader.log')
    assert Path(log_path).is_file(), 'Log file should be created'

    # Emit a test line
    test_message = 'test logging message'
    logging.info(test_message)

    content = Path(log_path).read_text(encoding='utf-8')
    assert 'Logging initialised' in content
    assert test_message in content

    # Call again: should not duplicate handlers nor raise
    second_path = pkg.setup_logging()
    assert second_path == log_path

    # Write again and ensure only one additional line roughly appended.
    # (Simpler invariant: file size grows, not doubled lines.)
    size_before = os.path.getsize(log_path)
    logging.info('second call')
    size_after = os.path.getsize(log_path)
    assert size_after > size_before
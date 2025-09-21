import os
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import torrent_downloader as pkg
from torrent_downloader import util


class TestLoggingSetup(unittest.TestCase):
    def setUp(self):  # noqa: D401
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        # Clear caches to avoid cross-test interference
        for fn in (util.get_app_data_dir, util.get_log_dir, util.get_cache_dir):
            try:
                fn.cache_clear()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover
                pass

    def tearDown(self):  # noqa: D401
        self.tmp.cleanup()

    def test_setup_logging_creates_file_and_is_idempotent(self):
        app_dir = self.tmp_path / 'appdata'
        log_dir = self.tmp_path / 'logs'
        cache_dir = self.tmp_path / 'cache'
        # Patching util helpers to return temp paths
        with patch('torrent_downloader.util.get_app_data_dir', new=lambda: str(app_dir)), \
             patch('torrent_downloader.util.get_log_dir', new=lambda: str(log_dir)), \
             patch('torrent_downloader.util.get_cache_dir', new=lambda: str(cache_dir)):
            log_path = pkg.setup_logging()
            self.assertTrue(log_path.endswith('torrentdownloader.log'))
            self.assertTrue(Path(log_path).is_file(), 'Log file should be created')

            test_message = 'test logging message'
            logging.info(test_message)
            content = Path(log_path).read_text(encoding='utf-8')
            self.assertIn('Logging initialised', content)
            self.assertIn(test_message, content)

            second_path = pkg.setup_logging()
            self.assertEqual(second_path, log_path)

            size_before = os.path.getsize(log_path)
            logging.info('second call')
            size_after = os.path.getsize(log_path)
            self.assertGreater(size_after, size_before)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

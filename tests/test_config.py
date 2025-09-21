import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from torrent_downloader import config, util


class TestConfig(unittest.TestCase):
    def setUp(self):  # noqa: D401
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        # Clear cache to ensure fresh path each test
        try:
            util.get_app_data_dir.cache_clear()  # type: ignore[attr-defined]
        except Exception:
            pass

    def tearDown(self):  # noqa: D401
        try:
            util.get_app_data_dir.cache_clear()  # type: ignore[attr-defined]
        except Exception:
            pass
        self.tmp.cleanup()

    def test_save_and_load_download_directory(self):
        app_dir = self.tmp_path / 'appdata'
        app_dir.mkdir()
        with patch('torrent_downloader.config.util.get_app_data_dir', new=lambda: str(app_dir)):
            target_dir = str(self.tmp_path / 'downloads')
            config.save_download_directory(target_dir)
            cfg_file = Path(config.get_config_file_path())
            self.assertTrue(cfg_file.is_file())
            raw = json.loads(cfg_file.read_text())
            self.assertEqual(raw['download_directory'], target_dir)
            loaded = config.load_download_directory()
            self.assertEqual(loaded, target_dir)

    def test_load_download_directory_missing(self):
        app_dir = self.tmp_path / 'appdata2'
        app_dir.mkdir()
        with patch('torrent_downloader.config.util.get_app_data_dir', new=lambda: str(app_dir)):
            self.assertIsNone(config.load_download_directory())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

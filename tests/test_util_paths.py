import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from torrent_downloader import util

ALL_CACHED = [
    util.get_app_data_dir,
    util.get_log_dir,
    util.get_cache_dir,
    util.get_downloads_dir,
    util.get_fallback_downloads_dir,
]


def _clear_caches():
    for fn in ALL_CACHED:
        try:  # pragma: no cover
            fn.cache_clear()  # type: ignore[attr-defined]
        except Exception:
            pass


class TestUtilPaths(unittest.TestCase):
    def setUp(self):  # noqa: D401
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self._environ_backup = os.environ.copy()
        _clear_caches()

    def tearDown(self):  # noqa: D401
        _clear_caches()
        os.environ.clear()
        os.environ.update(self._environ_backup)
        self.tmp.cleanup()

    # --- Platform directory helpers ---
    def test_app_log_cache_dirs_linux(self):
        fake_home = self.tmp_path / 'home'
        (fake_home / '.config').mkdir(parents=True)
        os.environ['HOME'] = str(fake_home)
        with patch('torrent_downloader.util.sys.platform', 'linux'):
            app_dir = fake_home / '.local' / 'share' / util.APP_NAME
            cache_dir = fake_home / '.cache' / util.APP_NAME
            self.assertEqual(util.get_app_data_dir(), str(app_dir))
            self.assertEqual(util.get_log_dir(), str(app_dir / 'logs'))
            self.assertEqual(util.get_cache_dir(), str(cache_dir))

    def test_app_dirs_windows(self):
        local_app_data = self.tmp_path / 'LOCALAPPDATA'
        os.environ['LOCALAPPDATA'] = str(local_app_data)
        with patch('torrent_downloader.util.sys.platform', 'win32'):
            expected_app = local_app_data / util.APP_NAME
            self.assertEqual(util.get_app_data_dir(), str(expected_app))
            self.assertEqual(util.get_log_dir(), str(expected_app / 'Logs'))
            self.assertEqual(util.get_cache_dir(), str(expected_app / 'Cache'))
            self.assertEqual(util.get_fallback_downloads_dir(), str(expected_app / 'Downloads'))

    def test_app_dirs_darwin(self):
        fake_home = self.tmp_path / 'home'
        (fake_home / 'Library' / 'Application Support').mkdir(parents=True)
        (fake_home / 'Library' / 'Logs').mkdir(parents=True)
        (fake_home / 'Library' / 'Caches').mkdir(parents=True)
        os.environ['HOME'] = str(fake_home)
        with patch('torrent_downloader.util.sys.platform', 'darwin'):
            app_expected = fake_home / 'Library' / 'Application Support' / util.APP_NAME
            log_expected = fake_home / 'Library' / 'Logs' / util.APP_NAME
            cache_expected = fake_home / 'Library' / 'Caches' / util.APP_NAME
            self.assertEqual(util.get_app_data_dir(), str(app_expected))
            self.assertEqual(util.get_log_dir(), str(log_expected))
            self.assertEqual(util.get_cache_dir(), str(cache_expected))
            self.assertEqual(util.get_fallback_downloads_dir(), str(cache_expected / 'Downloads'))

    # --- Downloads directory strategy ---
    def test_get_downloads_dir_env_override(self):
        with patch('torrent_downloader.util.sys.platform', 'linux'):
            env_downloads = self.tmp_path / 'MyDownloads'
            os.environ['XDG_DOWNLOAD_DIR'] = str(env_downloads)
            expected = env_downloads / util.APP_NAME
            self.assertEqual(util.get_downloads_dir(), str(expected))

    def test_get_downloads_dir_xdg_config_file(self):
        with patch('torrent_downloader.util.sys.platform', 'linux'):
            fake_home = self.tmp_path / 'home'
            config_dir = fake_home / '.config'
            config_dir.mkdir(parents=True)
            user_dirs_file = config_dir / 'user-dirs.dirs'
            user_dirs_file.write_text('XDG_DOWNLOAD_DIR="$HOME/CustomDownloads"\n')
            os.environ['HOME'] = str(fake_home)
            os.environ.pop('XDG_DOWNLOAD_DIR', None)
            expected = fake_home / 'CustomDownloads' / util.APP_NAME
            self.assertEqual(util.get_downloads_dir(), str(expected))

    # --- ensure_app_dirs ---
    def test_ensure_app_dirs_basic_and_no_downloads(self):
        base = self.tmp_path / 'app'
        app_dir = base / 'data'
        log_dir = base / 'logs'
        cache_dir = base / 'cache'
        _clear_caches()
        with patch('torrent_downloader.util.get_app_data_dir', new=lambda: str(app_dir)), \
             patch('torrent_downloader.util.get_log_dir', new=lambda: str(log_dir)), \
             patch('torrent_downloader.util.get_cache_dir', new=lambda: str(cache_dir)), \
             patch('torrent_downloader.util.get_downloads_dir', new=lambda: str(base / 'downloads_primary')), \
             patch('torrent_downloader.util.get_fallback_downloads_dir', new=lambda: str(base / 'downloads_fallback')):
            created = util.ensure_app_dirs(create_downloads=True)
            self.assertEqual(set(created.keys()), {'app_data', 'log', 'cache', 'downloads'})
            for p in created.values():
                self.assertTrue(Path(p).is_dir())
            created2 = util.ensure_app_dirs(create_downloads=False)
            self.assertEqual(set(created2.keys()), {'app_data', 'log', 'cache'})

    def test_ensure_app_dirs_downloads_fallback(self):
        base = self.tmp_path / 'root'
        app_dir = base / 'data'
        log_dir = base / 'logs'
        cache_dir = base / 'cache'
        primary_downloads = base / 'downloads_primary'
        fallback_downloads = base / 'downloads_fallback'
        _clear_caches()
        # Create a FILE at the primary downloads path so mkdir will fail
        primary_downloads.parent.mkdir(parents=True, exist_ok=True)
        primary_downloads.write_text('sentinel file making mkdir fail')
        with patch('torrent_downloader.util.get_app_data_dir', new=lambda: str(app_dir)), \
             patch('torrent_downloader.util.get_log_dir', new=lambda: str(log_dir)), \
             patch('torrent_downloader.util.get_cache_dir', new=lambda: str(cache_dir)), \
             patch('torrent_downloader.util.get_downloads_dir', new=lambda: str(primary_downloads)), \
             patch('torrent_downloader.util.get_fallback_downloads_dir', new=lambda: str(fallback_downloads)):
            paths = util.ensure_app_dirs(create_downloads=True)
            self.assertEqual(paths['downloads'], str(fallback_downloads))
            self.assertTrue(Path(fallback_downloads).is_dir())
            # Primary path should remain a file, not directory
            self.assertTrue(primary_downloads.is_file())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

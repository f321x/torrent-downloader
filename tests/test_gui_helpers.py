import unittest
from torrent_downloader.gui import TorrentDownloaderApp, MAX_NAME_LEN


class TestGuiHelpers(unittest.TestCase):
    def test_format_eta_none(self):
        self.assertEqual(TorrentDownloaderApp._format_eta(None), "N/A")

    def test_format_eta_values(self):
        self.assertEqual(TorrentDownloaderApp._format_eta(3723), "1:02:03")

    def test_shorten(self):
        name = "a" * (MAX_NAME_LEN + 10)
        shortened = TorrentDownloaderApp._shorten(name)
        self.assertEqual(len(shortened), MAX_NAME_LEN)
        self.assertTrue(shortened.endswith("..."))
        short = "short name"
        self.assertEqual(TorrentDownloaderApp._shorten(short), short)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

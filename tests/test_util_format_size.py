import unittest
from torrent_downloader import util


class TestFormatSize(unittest.TestCase):
    def test_format_size_basic_ranges(self):
        self.assertEqual(util.format_size(0), "0.0 B")
        self.assertEqual(util.format_size(500), "500.0 B")
        self.assertEqual(util.format_size(1024), "1.0 KB")
        self.assertEqual(util.format_size(1024 * 1024), "1.0 MB")

    def test_format_size_gigabytes_and_overflow(self):
        one_gb = 1024 ** 3
        self.assertEqual(util.format_size(one_gb), "1.0 GB")
        self.assertEqual(util.format_size(int(2.5 * one_gb)), "2.5 GB")
        self.assertEqual(util.format_size(1024 ** 4), "1.0 TB")

    def test_format_size_edge_inputs(self):
        # Negative clamped
        self.assertEqual(util.format_size(-123), "0.0 B")
        # String numeric
        self.assertEqual(util.format_size("2048"), "2.0 KB")
        # Non-numeric string -> treated as 0
        self.assertEqual(util.format_size("not-a-number"), "0.0 B")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

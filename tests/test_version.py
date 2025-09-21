"""Test version information."""

import unittest

from torrent_downloader import __version__


class TestVersion(unittest.TestCase):
    def test_version_string(self):
        """Test that version is a string."""
        self.assertIsInstance(__version__, str)
        self.assertEqual(__version__, "0.0.1")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

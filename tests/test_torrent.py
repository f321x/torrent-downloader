import unittest
from unittest.mock import MagicMock, patch

# We need to patch libtorrent before importing the module that uses it
with patch('torrent_downloader.torrent.lt', new=MagicMock()) as mock_lt:
    # Mock the states enum
    mock_lt.torrent_status.states.checking_files = 1
    mock_lt.torrent_status.states.downloading_metadata = 2
    mock_lt.torrent_status.states.downloading = 3
    mock_lt.torrent_status.states.finished = 4
    mock_lt.torrent_status.states.seeding = 5
    mock_lt.torrent_status.states.allocating = 6
    mock_lt.torrent_status.states.checking_resume_data = 7

    from torrent_downloader.torrent import _get_state_str

class TestTorrent(unittest.TestCase):

    def test_get_state_str_checking_files(self):
        mock_status = MagicMock()
        mock_status.state = 1 # checking_files
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "checking")

    def test_get_state_str_downloading_metadata(self):
        mock_status = MagicMock()
        mock_status.state = 2 # downloading_metadata
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "metadata")

    def test_get_state_str_downloading(self):
        mock_status = MagicMock()
        mock_status.state = 3 # downloading
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "downloading")

    def test_get_state_str_finished(self):
        mock_status = MagicMock()
        mock_status.state = 4 # finished
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "finished")

    def test_get_state_str_seeding(self):
        mock_status = MagicMock()
        mock_status.state = 5 # seeding
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "seeding")

    def test_get_state_str_allocating(self):
        mock_status = MagicMock()
        mock_status.state = 6 # allocating
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "allocating")

    def test_get_state_str_checking_resume_data(self):
        mock_status = MagicMock()
        mock_status.state = 7 # checking_resume_data
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "checking resume")

    def test_get_state_str_paused(self):
        mock_status = MagicMock()
        mock_status.state = 3 # downloading, but paused
        mock_status.paused = True
        self.assertEqual(_get_state_str(mock_status), "paused")

    def test_get_state_str_unknown_state(self):
        mock_status = MagicMock()
        mock_status.state = 99 # unknown state
        mock_status.paused = False
        self.assertEqual(_get_state_str(mock_status), "99")

    def test_get_state_str_libtorrent_not_available(self):
        # Temporarily set lt to None to simulate it not being available
        with patch('torrent_downloader.torrent.lt', None):
            mock_status = MagicMock()
            mock_status.state = 3
            mock_status.paused = False
            self.assertEqual(_get_state_str(mock_status), "N/A")

if __name__ == '__main__':
    unittest.main()

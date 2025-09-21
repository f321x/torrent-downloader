
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from torrent_downloader.torrent import TorrentManager

class TestSession(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = os.path.join(self.temp_dir, "session.dat")
        self.download_dir = os.path.join(self.temp_dir, "downloads")
        os.makedirs(self.download_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('torrent_downloader.torrent.lt')
    def test_session_save_and_load(self, mock_lt):
        # Mock libtorrent components
        mock_session_state_data = b"mock_session_state"
        mock_resume_data_payload = b"mock_resume_data_payload"
        mock_bencoded_resume_data = b"mock_bencoded_resume_data"

        # Mock for saving
        mock_lt.bencode.side_effect = [mock_session_state_data, mock_bencoded_resume_data]
        mock_lt.bdecode.return_value = mock_session_state_data # For loading session state

        mock_session = MagicMock()
        mock_lt.session.return_value = mock_session
        mock_session.save_state.return_value = {} # Empty dict for session state
        mock_session.wait_for_alert.return_value = None # Don't block test
        
        mock_lt.save_resume_data_alert = type("save_resume_data_alert", (object,), {}) # Mock as a type
        mock_alert = MagicMock()
        mock_alert.__class__ = mock_lt.save_resume_data_alert # Now this works
        mock_alert.resume_data = mock_resume_data_payload
        mock_session.pop_alerts.return_value = [mock_alert]

        # Mock a torrent handle
        mock_handle = MagicMock()
        mock_handle.is_valid.return_value = True
        mock_handle.info_hash.return_value = "test_info_hash"
        mock_handle.save_resume_data.return_value = None # save_resume_data is async
        mock_lt.make_magnet_uri.return_value = "magnet:?xt=urn:btih:test_info_hash"
        mock_session.add_magnet_uri.return_value = mock_handle

        # -- Phase 1: Create a session, add a torrent, and save state --
        manager1 = TorrentManager(self.download_dir, self.session_file)
        manager1.add_magnet("magnet:?xt=urn:btih:test_info_hash")
        manager1.save_state()

        # Assert save_state calls
        mock_session.save_state.assert_called_once()
        mock_lt.bencode.assert_any_call({}) # Session state
        mock_handle.save_resume_data.assert_called_once()
        mock_session.pop_alerts.assert_called_once()
        mock_lt.bencode.assert_any_call([mock_resume_data_payload]) # Resume data

        # -- Phase 2: Create a new session and load the state --
        mock_session2 = MagicMock()
        mock_lt.session.return_value = mock_session2
        mock_session2.get_torrents.return_value = [] # Should be empty initially

        # Mock for loading resume data
        mock_lt.bdecode.side_effect = [mock_session_state_data, [mock_resume_data_payload]] # Session state, then resume data list
        mock_atp = MagicMock() # add_torrent_params
        mock_lt.read_resume_data.return_value = mock_atp

        mock_loaded_handle = MagicMock()
        mock_loaded_handle.is_valid.return_value = True
        mock_loaded_handle.info_hash.return_value = "test_info_hash"
        mock_lt.make_magnet_uri.return_value = "magnet:?xt=urn:btih:test_info_hash"
        mock_session2.add_torrent.return_value = mock_loaded_handle

        manager2 = TorrentManager(self.download_dir, self.session_file)

        # Assert load_state calls
        mock_lt.bdecode.assert_any_call(mock_session_state_data) # Session state
        mock_lt.bdecode.assert_any_call(mock_bencoded_resume_data) # Resume data
        mock_lt.read_resume_data.assert_called_once_with(mock_resume_data_payload)
        mock_session2.add_torrent.assert_called_once_with(mock_atp)
        self.assertEqual(mock_atp.save_path, self.download_dir)

        # Check if the torrent is present in the new manager
        loaded_torrents = manager2.get_loaded_torrents_info()
        self.assertEqual(len(loaded_torrents), 1)
        self.assertEqual(loaded_torrents[0].info_hash, "test_info_hash")
        self.assertEqual(loaded_torrents[0].magnet_link, "magnet:?xt=urn:btih:test_info_hash")

if __name__ == '__main__':
    unittest.main()

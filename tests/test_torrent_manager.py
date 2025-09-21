import unittest
from unittest.mock import MagicMock, patch, mock_open
import os

# It's better to patch the library where it is used, not in sys.modules.
# We will patch 'torrent_downloader.torrent.lt' which is how the TorrentManager
# module sees libtorrent.

from torrent_downloader.torrent import TorrentManager

@patch('torrent_downloader.torrent.lt')
class TestTorrentManager(unittest.TestCase):

    def setUp(self):
        """Set up a new TorrentManager instance for each test.
        The mock_lt object is passed by the @patch decorator.
        We don't use it here but in the test methods themselves.
        """
        self.download_dir = '/tmp/downloads'
        self.session_file = '/tmp/session.dat'

    def test_init(self, mock_lt):
        """Test that the TorrentManager initializes correctly."""
        # We create the manager inside the test to have full control over the mock
        mock_session = MagicMock()
        mock_lt.session.return_value = mock_session

        # Instantiate the manager
        manager = TorrentManager(self.download_dir, self.session_file)

        # Check that a session is created
        mock_lt.session.assert_called_once()
        # Check that settings are applied
        mock_session.apply_settings.assert_called_once()
        # Check that it tries to load a session (this happens inside __init__)
        # Since we can't easily mock the internal call, we trust the next test
        # Check that the torrent list is fetched
        mock_session.get_torrents.assert_called_once()

    def test_add_magnet(self, mock_lt):
        """Test adding a magnet link."""
        manager = TorrentManager(self.download_dir, self.session_file)
        manager._handles = [] # Ensure handles is a real list for this test
        magnet_uri = "magnet:?xt=urn:btih:0123456789abcdef"
        
        mock_handle = MagicMock()
        mock_lt.add_magnet_uri.return_value = mock_handle
        
        manager.add_magnet(magnet_uri)
        
        mock_lt.add_magnet_uri.assert_called_once_with(
            manager._session, magnet_uri, manager._params
        )
        self.assertIn(mock_handle, manager._handles)

    @patch('os.path.isfile', return_value=True)
    def test_add_torrent_file(self, mock_isfile, mock_lt):
        """Test adding a torrent file."""
        manager = TorrentManager(self.download_dir, self.session_file)
        manager._handles = [] # Ensure handles is a real list for this test
        torrent_path = "/path/to/file.torrent"
        
        mock_info = MagicMock()
        mock_lt.torrent_info.return_value = mock_info
        mock_handle = MagicMock()
        manager._session.add_torrent.return_value = mock_handle
        
        manager.add_torrent_file(torrent_path)
        
        mock_isfile.assert_called_once_with(torrent_path)
        mock_lt.torrent_info.assert_called_once_with(torrent_path)
        expected_params = manager._params.copy()
        expected_params['ti'] = mock_info
        manager._session.add_torrent.assert_called_once_with(expected_params)
        self.assertIn(mock_handle, manager._handles)

    def test_add_torrent_file_not_found(self, mock_lt):
        """Test adding a torrent file that does not exist."""
        manager = TorrentManager(self.download_dir, self.session_file)
        manager._handles = [] # Ensure handles is a real list for this test
        with self.assertRaises(FileNotFoundError):
            manager.add_torrent_file("/non/existent/file.torrent")

    def test_remove_at(self, mock_lt):
        """Test removing a torrent without deleting files."""
        manager = TorrentManager(self.download_dir, self.session_file)
        manager._handles = [] # Ensure handles is a real list for this test
        mock_handle = MagicMock()
        manager._handles.append(mock_handle)
        
        result = manager.remove_at(0, delete_files=False)
        
        self.assertTrue(result)
        self.assertEqual(len(manager._handles), 0)
        manager._session.remove_torrent.assert_called_once_with(mock_handle)

    def test_remove_at_with_delete(self, mock_lt):
        """Test removing a torrent and deleting its files."""
        manager = TorrentManager(self.download_dir, self.session_file)
        manager._handles = [] # Ensure handles is a real list for this test
        mock_handle = MagicMock()
        manager._handles.append(mock_handle)
        
        result = manager.remove_at(0, delete_files=True)
        
        self.assertTrue(result)
        manager._session.remove_torrent.assert_called_once_with(mock_handle, mock_lt.options_t.delete_files)

    def test_pause_and_resume_at(self, mock_lt):
        """Test pausing and resuming a torrent."""
        manager = TorrentManager(self.download_dir, self.session_file)
        manager._handles = [] # Ensure handles is a real list for this test
        mock_handle = MagicMock()
        mock_handle.status.return_value.pausable = True
        mock_handle.status.return_value.paused = False
        manager._handles.append(mock_handle)
        
        # Test pausing a torrent that is not paused
        manager.pause_at(0)
        mock_handle.pause.assert_called_once()
        
        # Set the torrent to be paused
        mock_handle.status.return_value.paused = True
        
        # Test resuming a torrent that is paused
        manager.resume_at(0)
        mock_handle.resume.assert_called_once()


    @patch("builtins.open", new_callable=mock_open)
    def test_save_state(self, mock_file, mock_lt):
        """Test that session state is saved correctly."""
        manager = TorrentManager(self.download_dir, self.session_file)
        mock_session_dict = {'test': 'state'}
        manager._session.save_state.return_value = mock_session_dict
        
        manager.save_state()
        
        manager._session.save_state.assert_called_once()
        mock_file.assert_called_once_with(self.session_file, 'wb')
        mock_lt.bencode.assert_called_once_with(mock_session_dict)
        mock_file().write.assert_called_once_with(mock_lt.bencode.return_value)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=b'd1:a1:bee')
    def test_load_state(self, mock_file, mock_exists, mock_lt):
        """Test that session state is loaded correctly."""
        # This test needs to check the behavior during __init__
        mock_session = MagicMock()
        mock_lt.session.return_value = mock_session
        mock_lt.bdecode.return_value = {'a': 'b'}

        manager = TorrentManager(self.download_dir, self.session_file)
        
        mock_exists.assert_called_with(self.session_file)
        mock_file.assert_called_with(self.session_file, 'rb')
        mock_lt.bdecode.assert_called_with(b'd1:a1:bee')
        mock_session.load_state.assert_called_with({'a': 'b'})

if __name__ == '__main__':
    unittest.main()
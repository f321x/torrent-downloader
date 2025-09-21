
import unittest
from unittest.mock import MagicMock, patch

# Mock tkinter before it's imported
with patch.dict('sys.modules', {'tkinter': MagicMock(), 'tkinter.ttk': MagicMock()}):
    from torrent_downloader.gui import TorrentDownloaderApp
    from torrent_downloader.torrent import TorrentStatus

class TestGuiLogic(unittest.TestCase):

    @patch('torrent_downloader.gui.TorrentManager')
    @patch('torrent_downloader.gui.util')
    def setUp(self, mock_util, mock_manager):
        """Set up a TorrentDownloaderApp with mocked dependencies."""
        # Mock the master tkinter window
        self.master = MagicMock()
        
        # Prevent the app from scheduling updates
        self.master.after = MagicMock()
        
        # Instantiate the app
        self.app = TorrentDownloaderApp(self.master)
        
        # Replace the manager with a mock for testing calls
        self.app.manager = self.mock_manager = MagicMock()
        # Replace the treeview with a mock as well
        self.app.tree = MagicMock()

    def test_build_rows_no_torrents(self):
        """Test that the correct placeholder row is built when there are no torrents."""
        rows = self.app._build_rows([])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "No active torrents")

    def test_build_rows_with_torrents(self):
        """Test that torrent status objects are correctly formatted into rows."""
        # Create a couple of fake TorrentStatus objects
        status1 = TorrentStatus(
            name="test_torrent_1.iso",
            progress=0.5,
            download_rate=102400, # 100 KB/s
            upload_rate=10240,   # 10 KB/s
            num_peers=10,
            eta_seconds=125,
            has_metadata=True,
            state='downloading'
        )
        status2 = TorrentStatus(
            name="test_torrent_2.zip",
            progress=1.0,
            download_rate=0,
            upload_rate=20480, # 20 KB/s
            num_peers=5,
            eta_seconds=None,
            has_metadata=True,
            state='seeding'
        )
        
        rows = self.app._build_rows([status1, status2])
        
        self.assertEqual(len(rows), 2)
        
        # Check row 1 (downloading torrent)
        row1 = rows[0]
        self.assertEqual(row1[0], "test_torrent_1.iso")
        self.assertEqual(row1[1], "50.0%") # Progress
        self.assertIn("100.0 KB/s", row1[2]) # Speed
        self.assertEqual(row1[3], "0:02:05") # ETA
        self.assertEqual(row1[4], "10") # Peers
        self.assertEqual(row1[5], "downloading") # State
        
        # Check row 2 (seeding torrent)
        row2 = rows[1]
        self.assertEqual(row2[0], "test_torrent_2.zip")
        self.assertEqual(row2[1], "100.0%")
        self.assertIn("20.0 KB/s", row2[2])
        self.assertEqual(row2[3], "N/A") # ETA for seeding
        self.assertEqual(row2[5], "seeding")

    def test_pause_resume_selected(self):
        """Test the logic for pausing and resuming selected torrents."""
        # Mock the tree selection to return two item IDs
        self.app.tree.selection.return_value = ('I001', 'I003')
        # Mock the order of children in the tree
        self.app.tree.get_children.return_value = ('I001', 'I002', 'I003')
        
        # Test pause
        self.app.pause_selected()
        # It should have called pause_at for index 0 and 2
        self.mock_manager.pause_at.assert_any_call(0)
        self.mock_manager.pause_at.assert_any_call(2)
        self.assertEqual(self.mock_manager.pause_at.call_count, 2)
        
        # Test resume
        self.app.resume_selected()
        # It should have called resume_at for index 0 and 2
        self.mock_manager.resume_at.assert_any_call(0)
        self.mock_manager.resume_at.assert_any_call(2)
        self.assertEqual(self.mock_manager.resume_at.call_count, 2)

    @patch('torrent_downloader.gui.messagebox')
    def test_remove_selected(self, mock_messagebox):
        """Test the logic for removing a selected torrent."""
        # Mock the tree selection and children order
        self.app.tree.selection.return_value = ('I002',)
        self.app.tree.get_children.return_value = ('I001', 'I002', 'I003')
        
        # Mock the confirmation dialog to return True (Yes)
        mock_messagebox.askyesno.return_value = True
        
        self.app.remove_selected(delete_files=False)
        
        # Verify it asked for confirmation
        mock_messagebox.askyesno.assert_called_once()
        # Verify the manager's remove_at was called for the correct index (1)
        self.mock_manager.remove_at.assert_called_once_with(1, delete_files=False)

    @patch('torrent_downloader.gui.messagebox')
    def test_remove_selected_cancelled(self, mock_messagebox):
        """Test that nothing is removed if the user cancels the dialog."""
        self.app.tree.selection.return_value = ('I002',)
        self.app.tree.get_children.return_value = ('I001', 'I002', 'I003')
        
        # Mock the confirmation dialog to return False (No)
        mock_messagebox.askyesno.return_value = False
        
        self.app.remove_selected()
        
        # Verify the manager's remove_at was NEVER called
        self.mock_manager.remove_at.assert_not_called()

if __name__ == '__main__':
    unittest.main()

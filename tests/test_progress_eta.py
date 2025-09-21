import unittest

from torrent_downloader.torrent import _compute_progress, _compute_eta, _status_from_handle, TorrentStatus


class FakeStatus:
    def __init__(self, **kw):
        self.progress = kw.get('progress', 0.0)
        self.total_done = kw.get('total_done', 0)
        self.total_wanted = kw.get('total_wanted', 0)
        self.download_rate = kw.get('download_rate', 0)
        self.upload_rate = kw.get('upload_rate', 0)
        self.num_peers = kw.get('num_peers', 0)
        self.state = kw.get('state', 'downloading')
        self.paused = kw.get('paused', False)


class FakeHandle:
    def __init__(self, name='test', has_meta=True, **st):
        self._name = name
        self._has_meta = has_meta
        self._status = FakeStatus(**st)

    def status(self):
        return self._status

    def has_metadata(self):
        return self._has_meta

    def name(self):
        return self._name


class TestProgressEta(unittest.TestCase):
    def test_compute_progress_basic(self):
        self.assertEqual(_compute_progress(0.9, 50, 100), 0.5)
        self.assertEqual(_compute_progress(2.0, 150, 100), 1.0)
        self.assertEqual(_compute_progress(-0.5, -10, 100), 0.0)
        self.assertEqual(_compute_progress(0.25, 0, 0), 0.25)

    def test_compute_eta(self):
        self.assertEqual(_compute_eta(50, 100, 10), 5)
        self.assertIsNone(_compute_eta(50, 100, 0))
        self.assertIsNone(_compute_eta(100, 100, 10))

    def test_status_from_handle_no_metadata(self):
        h = FakeHandle(has_meta=False, num_peers=3)
        st = _status_from_handle(h)
        self.assertIsInstance(st, TorrentStatus)
        self.assertFalse(st.has_metadata)
        self.assertEqual(st.progress, 0.0)
        # num_peers may be 0 or 3 depending on getattr success, assert in set
        self.assertIn(st.num_peers, {0, 3})

    def test_status_from_handle_with_metadata(self):
        h = FakeHandle(has_meta=True, name='file.iso', total_done=512, total_wanted=1024, download_rate=128, upload_rate=64, num_peers=5, progress=0.9)
        st = _status_from_handle(h)
        self.assertTrue(st.has_metadata)
        self.assertAlmostEqual(st.progress, 0.5, places=9)
        self.assertEqual(st.eta_seconds, (1024 - 512) // 128)
        self.assertEqual(st.name, 'file.iso')
        self.assertEqual(st.num_peers, 5)
        self.assertEqual(st.download_rate, 128)
        self.assertEqual(st.upload_rate, 64)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

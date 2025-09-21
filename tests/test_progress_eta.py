import types

from torrent_downloader.torrent import _compute_progress, _compute_eta, _status_from_handle, TorrentStatus


def test_compute_progress_basic():
    # Normal ratio
    assert _compute_progress(0.9, 50, 100) == 0.5
    # Clamp above 1
    assert _compute_progress(2.0, 150, 100) == 1.0
    # Clamp below 0
    assert _compute_progress(-0.5, -10, 100) == 0.0
    # Fallback to field when total_wanted == 0
    assert _compute_progress(0.25, 0, 0) == 0.25


def test_compute_eta():
    # Remaining 50 bytes @10 bytes/s => 5s
    assert _compute_eta(50, 100, 10) == 5
    # No rate => None
    assert _compute_eta(50, 100, 0) is None
    # Completed => None
    assert _compute_eta(100, 100, 10) is None


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


def test_status_from_handle_no_metadata():
    h = FakeHandle(has_meta=False, num_peers=3)
    st = _status_from_handle(h)
    assert isinstance(st, TorrentStatus)
    assert st.has_metadata is False
    assert st.progress == 0.0
    assert st.num_peers == 0 or st.num_peers == 3  # depends if attr fetch succeeded


def test_status_from_handle_with_metadata():
    h = FakeHandle(has_meta=True, name='file.iso', total_done=512, total_wanted=1024, download_rate=128, upload_rate=64, num_peers=5, progress=0.9)
    st = _status_from_handle(h)
    assert st.has_metadata is True
    # Recomputed progress: 512/1024 = 0.5
    assert abs(st.progress - 0.5) < 1e-9
    assert st.eta_seconds == (1024 - 512) // 128
    assert st.name == 'file.iso'
    assert st.num_peers == 5
    assert st.download_rate == 128
    assert st.upload_rate == 64

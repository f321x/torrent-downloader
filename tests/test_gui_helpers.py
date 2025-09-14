from torrent_downloader.gui import TorrentDownloaderApp, MAX_NAME_LEN


def test_format_eta_none():
    assert TorrentDownloaderApp._format_eta(None) == "N/A"


def test_format_eta_values():
    # 1 hour, 2 minutes, 3 seconds -> 1:02:03
    assert TorrentDownloaderApp._format_eta(3723) == "1:02:03"


def test_shorten():
    name = "a" * (MAX_NAME_LEN + 10)
    shortened = TorrentDownloaderApp._shorten(name)
    assert len(shortened) == MAX_NAME_LEN
    assert shortened.endswith("...")

    short = "short name"
    assert TorrentDownloaderApp._shorten(short) == short

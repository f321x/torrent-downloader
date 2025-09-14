from torrent_downloader import util


def test_format_size_basic_ranges():
    assert util.format_size(0) == "0.0 B"
    assert util.format_size(500) == "500.0 B"
    # 1024 bytes => 1.0 KB (binary progression)
    assert util.format_size(1024) == "1.0 KB"
    # 1 MiB
    assert util.format_size(1024 * 1024) == "1.0 MB"


def test_format_size_gigabytes_and_overflow():
    one_gb = 1024 ** 3
    assert util.format_size(one_gb) == "1.0 GB"
    # 2.5 GB
    assert util.format_size(int(2.5 * one_gb)) == "2.5 GB"
    # Something very large (>= TB)
    assert util.format_size(1024 ** 4) == "1.0 TB"

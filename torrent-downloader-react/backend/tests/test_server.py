from fastapi.testclient import TestClient
import pytest
from torrent_downloader.server import app

client = TestClient(app)

def test_read_root():
    """Test that the root endpoint serves the index.html file."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_downloads_path():
    """Test that the downloads path endpoint returns a valid path."""
    response = client.get("/api/downloads/path")
    assert response.status_code == 200
    data = response.json()
    assert "path" in data
    assert isinstance(data["path"], str)
    assert "TorrentDownloader" in data["path"]

def test_add_invalid_torrent():
    """Test that adding an invalid magnet link returns an error."""
    response = client.post(
        "/api/torrent/add",
        json={"magnet_link": "invalid_magnet_link"}
    )
    assert response.status_code == 400

def test_list_torrents():
    """Test that listing torrents returns a valid response."""
    response = client.get("/api/torrent/list")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) 
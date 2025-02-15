from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
from torrent_downloader.server import app, static_dir

# Create a pytest fixture to handle static directory setup
@pytest.fixture(autouse=True)
def setup_static_dir(tmp_path):
    """Create temporary static directories for testing."""
    # Create temporary static directories
    test_static = tmp_path / "static"
    test_static.mkdir()
    test_assets = test_static / "assets"
    test_assets.mkdir()
    
    # Create a dummy index.html
    with open(test_static / "index.html", "w") as f:
        f.write("<html><body>Test</body></html>")
    
    # Create a dummy favicon.ico
    with open(test_static / "favicon.ico", "wb") as f:
        f.write(b"")
    
    # Patch the static_dir path
    with patch("torrent_downloader.server.static_dir", test_static):
        yield

# Create the test client
client = TestClient(app)

def test_read_root(setup_static_dir):
    """Test that the root endpoint serves the index.html file."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"<html><body>Test</body></html>" in response.content

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
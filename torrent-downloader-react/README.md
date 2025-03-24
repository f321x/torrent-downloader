# Torrent Downloader Web App

A modern, full-featured torrent downloader with a clean React interface and FastAPI backend.

![Torrent Downloader Web UI](https://github.com/stevenyyan/torrent-downloader/raw/main/torrent-downloader-react/screenshots/webapp_screenshot.png)

## Features

- **Sleek, Responsive UI**: Modern React interface that works on desktop and mobile
- **Real-time Updates**: Live tracking of download progress, speed, and ETA
- **Easy to Use**: Simple interface for adding and managing downloads
- **Flexible Backend**: Powerful FastAPI server handling torrent operations
- **Lightweight**: Minimal resource usage while maintaining full functionality
- **Cross-platform**: Works on Windows, macOS, and Linux

## System Requirements

- Python 3.8 or higher
- Platform-specific libtorrent dependencies:
  - **Windows**: Microsoft Visual C++ Redistributable
  - **macOS**: `brew install libtorrent-rasterbar`
  - **Ubuntu/Debian**: `sudo apt-get install python3-libtorrent`
  - **Fedora**: `sudo dnf install rb_libtorrent-python3`

## Installation

### From PyPI (Recommended)

```bash
pip install torrent-downloader-react
```

### From Source

```bash
git clone https://github.com/stevenyyan/torrent-downloader.git
cd torrent-downloader/torrent-downloader-react/backend
pip install -e .
```

## Usage

1. Start the application:
   ```bash
   torrent-downloader-react
   ```
2. Open your browser at http://127.0.0.1:8000
3. Paste a magnet link in the input field and click "Add Torrent"
4. Monitor download progress in the list view
5. Access completed downloads in your Downloads/TorrentDownloader folder
6. Click "Open Download Folder" to view your downloaded files

## Development Setup

### Frontend (React + Vite)

```bash
# Install dependencies
cd torrent-downloader-react
npm install

# Start development server (runs on http://localhost:5173)
npm run dev
```

### Backend (FastAPI)

```bash
# Install dependencies
cd torrent-downloader-react/backend
pip install -r requirements.txt

# Start development server
python -m torrent_downloader.server
```

## API Documentation

The backend provides a RESTful API:

- `POST /api/torrent/add` - Add new torrent
- `GET /api/torrent/list` - List all active torrents
- `DELETE /api/torrent/{torrent_id}` - Remove torrent
- `GET /api/downloads/path` - Get downloads directory path
- `POST /api/downloads/open` - Open downloads folder

## Alternative Installation with Conda

```bash
# Create and activate conda environment
conda create -n torrent-env python=3.11
conda activate torrent-env

# Install libtorrent dependency
conda install -c conda-forge libtorrent

# Install the package
pip install torrent-downloader-react
```

## License

MIT License - See LICENSE file for details.

## Legal Notice

This software is intended for downloading legal torrents only. Users are responsible for compliance with applicable laws.

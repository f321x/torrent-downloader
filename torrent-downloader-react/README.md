# Torrent Downloader Web App

A modern, full-featured torrent downloader with a clean React interface and Python backend.

## Quick Start

```bash
pip install torrent-downloader-react
torrent-downloader-react  # Opens in browser at http://127.0.0.1:8000
```

## System Requirements

- Python 3.8+
- Platform-specific dependencies:
  - **Windows**: Microsoft Visual C++ Redistributable
  - **macOS**: `brew install libtorrent-rasterbar`
  - **Ubuntu/Debian**: `sudo apt-get install python3-libtorrent`
  - **Fedora**: `sudo dnf install rb_libtorrent-python3`

## Features

- Modern, responsive UI with dark mode
- Real-time download progress monitoring
- Download speed and ETA tracking
- Easy magnet link handling
- Cross-platform support
- Concurrent downloads

## Usage

1. Start the application:
   ```bash
   torrent-downloader-react
   ```
2. Open your browser at http://127.0.0.1:8000
3. Paste a magnet link and click "Add Torrent"
4. Monitor progress in the downloads list
5. Access completed downloads in your downloads folder

## Alternative Installation: Using Conda

```bash
conda create -n torrent-env python=3.11
conda activate torrent-env
conda install -c conda-forge libtorrent
pip install torrent-downloader-react
```

## Development

### Frontend (React)
```bash
# Install dependencies
cd torrent-downloader-react
npm install

# Start development server
npm run dev
```

### Backend (Python)
```bash
# Install dependencies
cd torrent-downloader-react/backend
pip install -r requirements.txt

# Start development server
python -m torrent_downloader.server
```

## API Documentation

The backend provides a RESTful API:

- `GET /api/torrents` - List all torrents
- `POST /api/torrents` - Add new torrent
- `DELETE /api/torrents/{id}` - Remove torrent
- `GET /api/torrents/{id}/status` - Get torrent status

## License

MIT License - See LICENSE file for details.

## Legal Notice

This software is intended for downloading legal torrents only. Users are responsible for compliance with applicable laws.

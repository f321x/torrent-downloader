# Torrent Downloader

A modern torrent downloading solution offering two implementations:

- 🌐 **Web Application** (`torrent-downloader-react`): Full-featured interface with real-time monitoring
- 📟 **CLI Tool** (`torrent-downloader-python`): Lightweight command-line downloader

## Quick Start

### System Requirements

- Python 3.8+
- Platform-specific dependencies:
  - **Windows**: Microsoft Visual C++ Redistributable
  - **macOS**: `brew install libtorrent-rasterbar`
  - **Ubuntu/Debian**: `sudo apt-get install python3-libtorrent`
  - **Fedora**: `sudo dnf install rb_libtorrent-python3`

### Web Application

```bash
pip install torrent-downloader-react
torrent-downloader-react  # Opens in browser at http://127.0.0.1:8000
```

### CLI Tool

```bash
pip install torrent-downloader-python
torrent-downloader-python "magnet:?xt=urn:btih:..."
```

## Features

### Web Application
- Modern UI with dark mode
- Real-time progress monitoring
- Easy magnet link handling
- Cross-platform support

### CLI Tool
- Lightweight and efficient
- Direct magnet link downloads
- Simple command-line interface

## Development Setup

### Web Application
```bash
cd torrent-downloader-react
npm install && npm run dev  # Frontend
cd backend && pip install -r requirements.txt && python -m torrent_downloader.server  # Backend
```

### CLI Tool
```bash
cd torrent-downloader-python
pip install -e .
```

## Project Structure

```
torrent-downloader/
├── torrent-downloader-react/   # Web application
│   ├── src/                    # React frontend
│   └── backend/                # Python backend
└── torrent-downloader-python/  # CLI application
```

## Alternative Installation: Using Conda

```bash
conda create -n torrent-env python=3.11
conda activate torrent-env
conda install -c conda-forge libtorrent
pip install torrent-downloader-react  # or torrent-downloader-python
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See LICENSE file for details.

## Legal Notice

This software is intended for downloading legal torrents only. Users are responsible for compliance with applicable laws. 
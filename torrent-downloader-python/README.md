# Torrent Downloader CLI

A lightweight command-line torrent downloader focused on simplicity and efficiency.

## Quick Start

```bash
pip install torrent-downloader-python
torrent-downloader-python "magnet:?xt=urn:btih:..."
```

## System Requirements

- Python 3.8+
- Platform-specific dependencies:
  - **Windows**: Microsoft Visual C++ Redistributable
  - **macOS**: `brew install libtorrent-rasterbar`
  - **Ubuntu/Debian**: `sudo apt-get install python3-libtorrent`
  - **Fedora**: `sudo dnf install rb_libtorrent-python3`

## Features

- Lightweight and efficient downloads
- Simple command-line interface
- Cross-platform support
- Direct magnet link handling
- Progress monitoring

## Usage

```bash
# Basic usage with magnet link
torrent-downloader-python "magnet:?xt=urn:btih:..."

# Specify download directory
torrent-downloader-python --output ~/Downloads "magnet:?xt=urn:btih:..."

# Set download speed limit (in KB/s)
torrent-downloader-python --speed-limit 1000 "magnet:?xt=urn:btih:..."
```

## Alternative Installation: Using Conda

```bash
conda create -n torrent-env python=3.11
conda activate torrent-env
conda install -c conda-forge libtorrent
pip install torrent-downloader-python
```

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/torrent-downloader.git
cd torrent-downloader/torrent-downloader-python

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## License

MIT License - See LICENSE file for details.

## Legal Notice

This software is intended for downloading legal torrents only. Users are responsible for compliance with applicable laws. 
# Torrent Downloader Desktop App

A lightweight, cross-platform torrent downloader with a native GUI built using Python and Tkinter.

![Torrent Downloader GUI](https://github.com/stevenbtc/torrent-downloader/raw/main/torrent-downloader-python/screenshots/app_screenshot.png)

## Features

- Simple, intuitive graphical interface
- Direct magnet link downloads
- Real-time download progress tracking
- Customizable download location
- Automatic torrent metadata fetching
- Cross-platform compatibility (Windows, macOS, Linux)
- Low system resource consumption

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
pip install torrent-downloader-python
```

### From Source

```bash
git clone https://github.com/stevenbtc/torrent-downloader.git
cd torrent-downloader/torrent-downloader-python
pip install -e .
```

## Usage

### Launch the GUI

```bash
# Start the application
torrent-downloader-python
```

### Using the Application

1. Launch the application
2. Paste a magnet link into the input field
3. Click "Add Torrent" to begin downloading
4. Monitor progress in the main window
5. Access completed downloads through the "Open Download Folder" option

## Alternative Installation with Conda

For users who prefer Conda environments:

```bash
# Create and activate conda environment
conda create -n torrent-env python=3.11
conda activate torrent-env

# Install libtorrent dependency
conda install -c conda-forge libtorrent

# Install the package
pip install torrent-downloader-python
```

## Development

```bash
# Clone repository
git clone https://github.com/stevenbtc/torrent-downloader.git
cd torrent-downloader/torrent-downloader-python

# Install in development mode
pip install -e .

# Run the application
python torrent_downloader_gui.py

# Run tests
python -m pytest tests/
```

## License

MIT License - See LICENSE file for details.

## Legal Notice

This software is intended for downloading legal torrents only. Users are responsible for compliance with applicable laws. 
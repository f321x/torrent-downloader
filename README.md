# Torrent Downloader Desktop App

A lightweight, cross-platform torrent downloader with a native GUI built using Python and Tkinter.
Forked from https://github.com/stevenyyan/torrent-downloader, thanks to Steven Yan for the base code.

![Torrent Downloader GUI](https://github.com/stevenyyan/torrent-downloader/raw/main/torrent-downloader-python/screenshots/app_screenshot.png)

## Goals

- Simple and readable code, making it easy to experiment with Bittorrent
- Simple, intuitive graphical interface
- Sufficient features for practical use
- No external dependencies except for libtorrent

## Warning

Large parts of this codebase are vibecoded. I try to sanity check and force the llm to write unittests,
however it's totally possible that some things are broken or don't make any sense at all.

## System Requirements

- Python 3.13 or higher
- Platform-specific libtorrent dependencies:
  - **Windows**: Microsoft Visual C++ Redistributable
  - **macOS**: `brew install libtorrent-rasterbar`
  - **Ubuntu/Debian**: `sudo apt-get install python3-libtorrent`
  - **Fedora**: `sudo dnf install rb_libtorrent-python3`

## Installation

### From Source

```bash
git clone https://github.com/f321x/torrent-downloader.git
cd torrent-downloader
pip install -e .
```

## Usage

### Launch the GUI

```bash
# Start the application
torrent-downloader
```

### Using the Application

1. Launch the application
2. Paste a magnet link into the input field
3. Click "Add Torrent" to begin downloading
4. Monitor progress in the main window
5. Access completed downloads through the "Open Downloads" button

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
git clone https://github.com/stevenyyan/torrent-downloader.git
cd torrent-downloader
pip install -e .

# Run the GUI
python main.py

# Run tests
pytest -q
```

### Adding New Functionality

When extending functionality, prefer adding logic to `torrent.py` (core) or `util.py` (helpers) rather than the GUI. Keep the GUI a thin layer.

## License

MIT License - See LICENSE file for details.

## Legal Notice

This software is intended for downloading legal torrents only. Users are responsible for compliance with applicable laws. 
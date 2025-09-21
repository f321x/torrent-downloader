# Torrent Downloader Desktop App

A lightweight, cross-platform torrent downloader with a native GUI built using Python and Tkinter.
Forked from https://github.com/stevenyyan/torrent-downloader, thanks to Steven Yan for the base code.

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
### Running tests

```bash
python -m unittest discover -v tests
```
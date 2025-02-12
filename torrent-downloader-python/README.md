# Torrent Downloader (Python Version)

A modern, cross-platform torrent downloading application with a clean and intuitive graphical interface.

## Features

- 🎯 Modern and intuitive graphical user interface
- 🔍 Easy magnet link handling
- 📊 Real-time download progress tracking
- 📈 Live download/upload speed monitoring
- 👥 Peer connection status
- ⏱️ Accurate ETA calculations
- 📁 Platform-specific download locations
- 🌍 Full cross-platform support (Windows, macOS, Linux)
- 🎨 High-resolution application icons
- 📝 Comprehensive logging system

## Installation

### Windows
1. Download the latest `TorrentDownloader.exe` from the releases page
2. Double-click to run the application
3. On first run, Windows may show a security prompt - click "More info" and "Run anyway"

### macOS
1. Download the latest `TorrentDownloader.app` from the releases page
2. Move to your Applications folder
3. Right-click and select "Open" (required only the first time due to security settings)
4. If you see "App can't be opened", go to System Preferences → Security & Privacy → General and click "Open Anyway"

### Linux
1. Download the latest `TorrentDownloader` AppImage from the releases page
2. Make it executable: `chmod +x TorrentDownloader.AppImage`
3. Double-click to run or execute from terminal

### Building from Source

#### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- libtorrent-rasterbar

#### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/torrent_downloader.git
   cd torrent_downloader/torrent-downloader-python
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Building

##### Windows
```bash
python convert_icons.py  # Generate icons
pyinstaller torrent_downloader_win.spec
```

##### macOS
```bash
python convert_icons.py  # Generate icons
pyinstaller torrent_downloader.spec
```

The packaged application will be created in the `dist` directory.

## Usage

1. Launch TorrentDownloader
2. Paste a magnet link into the text field
3. Click "Add Magnet" to start downloading
4. Monitor download progress in the main window
5. Access downloaded files through the "Open Downloads" button

## Default Download Locations

- Windows: `%USERPROFILE%\Downloads\TorrentDownloader`
- macOS: `~/Downloads/TorrentDownloader`
- Linux: `~/Downloads/TorrentDownloader` or `$XDG_DOWNLOAD_DIR/TorrentDownloader`

## License

MIT License - See LICENSE file for details 
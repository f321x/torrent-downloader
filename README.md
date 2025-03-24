# Torrent Downloader

A modern, lightweight solution for downloading torrents, offering two distinct implementations:

- 🌐 **Web Application** (`torrent-downloader-react`): Full-featured React interface with FastAPI backend
- 📟 **Desktop Application** (`torrent-downloader-python`): Native GUI built with Tkinter

## Features

### Web Application
- Modern React UI with clean design
- Real-time download progress tracking
- Download speed, ETA, and file size information
- Easy magnet link handling
- Cross-platform compatibility

### Desktop Application
- Lightweight native interface
- Simple, intuitive controls
- Direct magnet link downloads
- Progress monitoring and notifications
- Low resource consumption

## System Requirements

- Python 3.8 or higher
- Platform-specific libtorrent dependencies:
  - **Windows**: Microsoft Visual C++ Redistributable
  - **macOS**: `brew install libtorrent-rasterbar`
  - **Ubuntu/Debian**: `sudo apt-get install python3-libtorrent`
  - **Fedora**: `sudo dnf install rb_libtorrent-python3`

## Quick Start

### Web Application

```bash
# Install the package
pip install torrent-downloader-react

# Run the application (opens in browser at http://127.0.0.1:8000)
torrent-downloader-react
```

### Desktop Application

```bash
# Install the package
pip install torrent-downloader-python

# Launch the GUI application
torrent-downloader-python
```

## Development Setup

### Web Application
```bash
# Set up frontend
cd torrent-downloader-react
npm install
npm run dev  # Starts development server at http://localhost:5173

# Set up backend in a separate terminal
cd torrent-downloader-react/backend
pip install -r requirements.txt
python -m torrent_downloader.server
```

### Desktop Application
```bash
cd torrent-downloader-python
pip install -e .
python torrent_downloader_gui.py
```

## Project Structure

```
torrent-downloader/
├── torrent-downloader-react/   # Web application
│   ├── src/                    # React frontend
│   └── backend/                # FastAPI backend
└── torrent-downloader-python/  # Desktop application
    └── torrent_downloader/     # Python package
```

## Alternative Installation with Conda

```bash
# Create and activate conda environment
conda create -n torrent-env python=3.11
conda activate torrent-env

# Install libtorrent dependency
conda install -c conda-forge libtorrent

# Install desired package
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
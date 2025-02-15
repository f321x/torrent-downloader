# Torrent Downloader

A modern, user-friendly torrent downloader application built with React and Python.

## Features

- Clean, modern user interface
- Real-time download progress and speed monitoring
- Cross-platform support (Windows, macOS, Linux)
- Easy-to-use magnet link support
- Dark mode support

## Prerequisites

Before installing, make sure you have the required system dependencies:

### Windows
- Python 3.8 or higher
- Microsoft Visual C++ Redistributable (latest version)
- Libtorrent:
  ```bash
  # Option 1: Using pip
  pip install python-libtorrent

  # Option 2: Using conda
  conda install -c conda-forge libtorrent
  ```

### macOS
```bash
# Using Homebrew (recommended)
brew install libtorrent-rasterbar

# Or using conda
conda install -c conda-forge libtorrent
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-libtorrent

# Or using conda
conda install -c conda-forge libtorrent
```

### Linux (Fedora)
```bash
sudo dnf install rb_libtorrent-python3

# Or using conda
conda install -c conda-forge libtorrent
```

### Using Conda (All Platforms)
If you're using Conda, you can install libtorrent in your environment:
```bash
conda create -n torrent-env python=3.11
conda activate torrent-env
conda install -c conda-forge libtorrent
```

## Installation

### Method 1: Using pip (Recommended)

```bash
# 1. Install libtorrent (see Prerequisites section above)

# 2. Install the package
pip install torrent-downloader-react

# 3. Run the application
torrent-downloader-react
```

The application will start and open in your default web browser at http://127.0.0.1:8000

### Method 2: From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/torrent-downloader.git
cd torrent-downloader/torrent-downloader-react
```

2. Build the application:
```bash
cd backend
python build.py
```

3. Install the built package:
```bash
pip install dist/torrent-downloader-*.whl
```

4. Run the application:
```bash
torrent-downloader
```

## Usage

1. Start the application using one of the installation methods above
2. The application will open in your default web browser
3. Paste a magnet link into the input field
4. Click "Add Torrent" to start downloading
5. Monitor progress in the torrents list
6. Click "Open Downloads" to view your downloaded files

## Development

### Frontend (React)

```bash
cd torrent-downloader-react
npm install
npm run dev
```

### Backend (Python)

```bash
cd torrent-downloader-react/backend
pip install -r requirements.txt
python -m torrent_downloader.server
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for downloading legal torrents only. The authors are not responsible for any misuse of this software.

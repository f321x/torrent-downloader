# Torrent Downloader

A modern, user-friendly torrent downloader application with two implementations:
1. **torrent-downloader-react**: A full-featured web application built with React and Python
2. **torrent-downloader-python**: A lightweight command-line interface

## Features

### React Web Application
- Clean, modern user interface with dark mode support
- Real-time download progress and speed monitoring
- Cross-platform support (Windows, macOS, Linux)
- Easy-to-use magnet link support
- Built with React and FastAPI

### Python CLI
- Simple command-line interface
- Lightweight and efficient
- Cross-platform support
- Direct magnet link downloads

## Prerequisites

Before installing, make sure you have the required system dependencies:

### System Dependencies

#### Windows
- Python 3.8 or higher
- Microsoft Visual C++ Redistributable (latest version)

#### macOS
```bash
# Required: Install libtorrent system package
brew install libtorrent-rasterbar
```

#### Linux (Ubuntu/Debian)
```bash
# Required: Install libtorrent system package
sudo apt-get update
sudo apt-get install python3-libtorrent
```

#### Linux (Fedora)
```bash
# Required: Install libtorrent system package
sudo dnf install rb_libtorrent-python3
```

### Alternative Installation Methods

#### Using Conda (All Platforms)
If you're using Conda, you can install libtorrent in your environment:
```bash
conda create -n torrent-env python=3.11
conda activate torrent-env
conda install -c conda-forge libtorrent
```

## Installation

### React Web Application

```bash
# 1. Install system dependencies (see Prerequisites section above)

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install the package
pip install torrent-downloader-react

# 4. Run the application
torrent-downloader-react
```

The web application will start and open in your default web browser at http://127.0.0.1:8000

### Python CLI

```bash
# 1. Install system dependencies (see Prerequisites section above)

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install the package
pip install torrent-downloader-python

# 4. Run the CLI
torrent-downloader-python "magnet:?xt=urn:btih:..."
```

## Development

### React Web Application

1. Frontend (React):
```bash
cd torrent-downloader-react
npm install
npm run dev
```

2. Backend (Python):
```bash
cd torrent-downloader-react/backend
pip install -r requirements.txt
python -m torrent_downloader.server
```

### Python CLI

```bash
cd torrent-downloader-python
pip install -e .
python -m torrent_downloader "magnet:?xt=urn:btih:..."
```

## Project Structure

```
torrent-downloader/
├── torrent-downloader-react/     # React web application
│   ├── src/                      # React frontend source
│   ├── backend/                  # Python backend
│   │   ├── torrent_downloader/   # Backend package
│   │   ├── tests/               # Backend tests
│   │   └── build.py             # Build script
│   └── package.json             # Frontend dependencies
│
└── torrent-downloader-python/    # Python CLI application
    ├── torrent_downloader/       # CLI package
    ├── tests/                    # CLI tests
    └── setup.py                  # Package configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Use semantic versioning for releases

## Releases

Both packages are available on PyPI:
- [torrent-downloader-react](https://pypi.org/project/torrent-downloader-react/)
- [torrent-downloader-python](https://pypi.org/project/torrent-downloader-python/)

Windows and macOS executables are available in the [GitHub Releases](https://github.com/yourusername/torrent-downloader/releases) section.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for downloading legal torrents only. The authors are not responsible for any misuse of this software. 
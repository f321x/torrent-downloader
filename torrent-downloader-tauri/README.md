# Torrent Downloader (Tauri Version)

A modern, cross-platform torrent downloading application built with Rust, Tauri, and React.

## Features

- 🚀 High-performance Rust backend
- 🎯 Modern React frontend with TypeScript
- 🔍 Easy magnet link handling
- 📊 Real-time download progress tracking
- 📈 Live download/upload speed monitoring
- 👥 Peer connection status
- ⏱️ Accurate ETA calculations
- 📁 Platform-specific download locations
- 🌍 Full cross-platform support (Windows, macOS, Linux)
- 🎨 Modern, native look and feel
- 📝 Comprehensive logging system

## Prerequisites

- Rust (latest stable)
- Node.js (v18 or later)
- npm (v9 or later)
- Platform-specific build tools:
  - Windows: Microsoft Visual Studio C++ Build Tools
  - macOS: Xcode Command Line Tools
  - Linux: `build-essential` package

## Development Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/torrent_downloader.git
   cd torrent_downloader/torrent-downloader-tauri
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install Rust dependencies:
   ```bash
   cd src-tauri
   cargo build
   ```

4. Start the development server:
   ```bash
   npm run tauri dev
   ```

## Building

To create a production build:

```bash
npm run tauri build
```

The packaged application will be created in `src-tauri/target/release/bundle`.

## Architecture

- **Frontend**: React with TypeScript, using modern React patterns and hooks
- **Backend**: Rust with Tauri, handling all torrent operations
- **Communication**: Tauri IPC bridge for frontend-backend communication
- **Packaging**: Tauri's native bundler for creating platform-specific installers

## Default Download Locations

- Windows: `%USERPROFILE%\Downloads\TorrentDownloader`
- macOS: `~/Downloads/TorrentDownloader`
- Linux: `~/Downloads/TorrentDownloader` or `$XDG_DOWNLOAD_DIR/TorrentDownloader`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See LICENSE file for details 
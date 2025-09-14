import sys

from torrent_downloader.torrent_downloader import main

if __name__ == "__main__":
    # This GUI version does not accept command-line arguments.
    if len(sys.argv) > 1:
        print("Error: Do not provide magnet links as command-line arguments. Use the GUI to add magnet links.")
        sys.exit(1)
    main() 
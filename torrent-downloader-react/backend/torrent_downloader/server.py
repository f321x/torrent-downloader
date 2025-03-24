from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import libtorrent as lt
import os
import sys
import logging
from typing import Dict, List, Optional
import time
from pathlib import Path
import subprocess

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory containing the static files
static_dir = Path(__file__).parent / "static"

def setup_static_files():
    """Set up static file serving. Called after app creation."""
    if static_dir.exists():
        # Mount static files only if the directory exists
        if (static_dir / "assets").exists():
            app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(str(static_dir / "favicon.ico"))

# Set up platform-specific paths
def get_downloads_dir() -> Path:
    if sys.platform == 'win32':
        downloads = os.path.expanduser('~/Downloads')
    elif sys.platform == 'darwin':
        downloads = os.path.expanduser('~/Downloads')
    else:  # Linux and other Unix-like
        downloads = os.path.expanduser('~/Downloads')
    
    torrent_dir = Path(downloads) / 'TorrentDownloader'
    torrent_dir.mkdir(parents=True, exist_ok=True)
    return torrent_dir

def open_folder(path: str) -> bool:
    """Open the folder using the system's default file explorer."""
    try:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=True)
        else:  # Linux and other Unix-like
            subprocess.run(['xdg-open', path], check=True)
        return True
    except Exception as e:
        logging.error(f"Failed to open folder: {e}")
        return False

# Initialize download directory
DOWNLOAD_PATH = get_downloads_dir()

# Initialize libtorrent session
session = lt.session()
settings = session.get_settings()
settings['listen_interfaces'] = '0.0.0.0:6881'
session.apply_settings(settings)

# Store active torrents
active_torrents: Dict[str, lt.torrent_handle] = {}

class TorrentRequest(BaseModel):
    magnet_link: str

class TorrentInfo(BaseModel):
    id: str
    name: str
    progress: float
    download_speed: float
    upload_speed: float
    state: str
    total_size: int
    downloaded: int
    eta_seconds: Optional[int] = None

@app.post("/api/torrent/add")
async def add_torrent(request: TorrentRequest):
    try:
        # Add the torrent
        try:
            params = lt.parse_magnet_uri(request.magnet_link)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid magnet link format: {str(e)}")
        
        params.save_path = str(DOWNLOAD_PATH)
        
        # Check if torrent already exists with this hash
        torrent_hash = str(params.info_hash)
        if torrent_hash in active_torrents:
            raise HTTPException(status_code=409, detail="A duplicate torrent is already being downloaded")
        
        handle = session.add_torrent(params)
        
        # Wait for metadata
        timeout = 30
        start_time = time.time()
        while not handle.has_metadata():
            if time.time() - start_time > timeout:
                raise HTTPException(status_code=408, detail="Timeout waiting for torrent metadata")
            time.sleep(0.1)
        
        torrent_id = str(handle.info_hash())
        active_torrents[torrent_id] = handle
        
        # Get the torrent name for the response
        torrent_name = handle.status().name
        
        return {"id": torrent_id, "message": f"Torrent '{torrent_name}' added successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/torrent/list")
async def list_torrents() -> List[TorrentInfo]:
    result = []
    for torrent_id, handle in active_torrents.items():
        status = handle.status()
        
        # Get the state string
        state_str = "unknown"
        if status.state == lt.torrent_status.downloading:
            state_str = "downloading"
        elif status.state == lt.torrent_status.seeding:
            state_str = "seeding"
        elif status.state == lt.torrent_status.finished:
            state_str = "finished"
        elif status.state == lt.torrent_status.checking_files:
            state_str = "checking"
        
        logging.debug(f"Torrent {torrent_id} state: {state_str} (raw state: {status.state})")
        
        # Calculate ETA
        eta = None
        try:
            if state_str == "downloading":
                remaining_bytes = status.total_wanted - status.total_wanted_done
                if remaining_bytes <= 0:
                    eta = 0  # Download complete
                elif status.download_rate > 0:
                    eta = int(remaining_bytes / status.download_rate)
                else:
                    eta = None  # Can't calculate ETA with zero download rate
            elif state_str in ["finished", "seeding"]:
                eta = 0  # Already complete
            elif state_str == "checking":
                eta = None  # Can't estimate during checking
        except Exception as e:
            logging.error(f"Error calculating ETA for torrent {torrent_id}: {e}")
            eta = None
        
        info = TorrentInfo(
            id=torrent_id,
            name=handle.name(),
            progress=status.progress * 100,
            download_speed=status.download_rate / 1024,  # Convert to KB/s
            upload_speed=status.upload_rate / 1024,  # Convert to KB/s
            state=state_str,
            total_size=status.total_wanted,
            downloaded=status.total_wanted_done,
            eta_seconds=eta
        )
        result.append(info)
    
    return result

@app.delete("/api/torrent/{torrent_id}")
async def remove_torrent(torrent_id: str, delete_files: bool = False):
    if torrent_id not in active_torrents:
        raise HTTPException(status_code=404, detail="Torrent not found")
    
    handle = active_torrents[torrent_id]
    session.remove_torrent(handle, 1 if delete_files else 0)
    del active_torrents[torrent_id]
    
    return {"message": "Torrent removed successfully"}

@app.get("/api/downloads/path")
async def get_downloads_path():
    return {"path": str(DOWNLOAD_PATH)}

@app.post("/api/downloads/open")
async def open_downloads():
    success = open_folder(str(DOWNLOAD_PATH))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to open downloads folder")
    return {"message": "Downloads folder opened successfully"}

def main():
    """Entry point for the application."""
    import uvicorn
    setup_static_files()  # Set up static files before running
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main() 
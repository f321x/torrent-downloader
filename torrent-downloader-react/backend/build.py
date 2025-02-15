import os
import shutil
import subprocess
from pathlib import Path

def build_frontend():
    """Build the React frontend"""
    print("Building frontend...")
    frontend_dir = Path(__file__).parent.parent
    
    # Install dependencies
    subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    # Build the frontend
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
    
    # Copy the built files to the backend static directory
    static_dir = Path(__file__).parent / "torrent_downloader" / "static"
    if static_dir.exists():
        shutil.rmtree(static_dir)
    
    dist_dir = frontend_dir / "dist"
    shutil.copytree(dist_dir, static_dir)

def build_backend():
    """Build the Python backend"""
    print("Building backend...")
    backend_dir = Path(__file__).parent
    
    # Clean previous builds
    for dir_name in ["build", "dist", "torrent_downloader.egg-info"]:
        path = backend_dir / dir_name
        if path.exists():
            shutil.rmtree(path)
    
    # Build the package
    subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"], cwd=backend_dir, check=True)

def main():
    try:
        build_frontend()
        build_backend()
        print("Build completed successfully!")
    except Exception as e:
        print(f"Build failed: {e}")
        exit(1)

if __name__ == "__main__":
    main() 
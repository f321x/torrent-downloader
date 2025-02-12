
import os
import sys

def _fix_libtorrent():
    if sys.platform == 'darwin':
        # Get the base directory (where the .app bundle is)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        
        # Add all possible library paths
        library_paths = [
            os.path.join(base_dir, 'Frameworks'),
            os.path.join(base_dir, 'Resources'),
            os.path.join(base_dir, 'Resources', 'lib'),
            os.path.join(base_dir, 'Frameworks', 'libtorrent'),
            os.path.join(base_dir, 'Resources', 'libtorrent'),
        ]
        
        # Set DYLD_LIBRARY_PATH
        os.environ['DYLD_LIBRARY_PATH'] = ':'.join(
            path for path in library_paths if os.path.exists(path)
        )
        
        # Add to Python path
        for path in library_paths:
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
        
        # Print debug info
        print("Python path:", sys.path)
        print("DYLD_LIBRARY_PATH:", os.environ.get('DYLD_LIBRARY_PATH'))
        print("Current directory:", os.getcwd())
        print("Executable path:", sys.executable)
        
        # Try to locate libtorrent files
        for path in library_paths:
            if os.path.exists(path):
                print(f"Contents of {path}:")
                try:
                    print(os.listdir(path))
                except Exception as e:
                    print(f"Error listing {path}: {e}")

_fix_libtorrent()

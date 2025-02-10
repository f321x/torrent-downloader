
import os
import sys

def _fix_libtorrent():
    if sys.platform == 'darwin':
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        os.environ['DYLD_LIBRARY_PATH'] = os.path.join(base_dir, 'Frameworks')
        sys.path.insert(0, os.path.join(base_dir, 'Frameworks'))

_fix_libtorrent()

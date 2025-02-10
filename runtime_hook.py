
import os
import sys

def _fix_paths():
    if sys.platform == 'win32':
        base_dir = os.path.dirname(os.path.dirname(sys.executable))
        os.environ['PYTHONPATH'] = os.path.join(base_dir, 'lib')
        os.environ['PATH'] = os.path.join(base_dir, 'lib') + os.pathsep + os.environ.get('PATH', '')

_fix_paths()

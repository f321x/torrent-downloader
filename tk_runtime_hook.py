
import os
import sys

def _fix_tkinter():
    if sys.platform == 'darwin':
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        os.environ['TK_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tk.framework', 'Versions', 'Current', 'Resources')
        os.environ['TCL_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tcl.framework', 'Versions', 'Current', 'Resources')
        os.environ['TKPATH'] = os.path.join(base_dir, 'Frameworks')

_fix_tkinter()

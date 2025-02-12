
import os
import sys
import platform

def _fix_tkinter():
    if sys.platform == 'darwin':
        # Get the base directory (where the .app bundle is)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
            
            # Set Tk/Tcl library paths relative to the app bundle
            os.environ['TK_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tk', 'Resources')
            os.environ['TCL_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tcl', 'Resources')
            os.environ['TKPATH'] = os.path.join(base_dir, 'Frameworks')
            
            # Force disable all menu-related features
            os.environ['TK_SILENCE_DEPRECATION'] = '1'
            os.environ['TK_NO_NATIVE_MENUBAR'] = '1'
            os.environ['TKPATH'] = '/System/Library/Frameworks'
            
            # Use system Tcl/Tk frameworks
            os.environ['TCL_LIBRARY'] = '/System/Library/Frameworks/Tcl.framework/Versions/Current/Resources'
            os.environ['TK_LIBRARY'] = '/System/Library/Frameworks/Tk.framework/Versions/Current/Resources'
            
            # Additional environment variables to control Tk behavior
            os.environ['TK_COCOA_FORCE_WINDOW_MENU'] = '0'
            os.environ['TK_COCOA_USE_SYSTEM_MENUBAR'] = '0'
            os.environ['TK_COCOA_DISABLE_MENUBAR'] = '1'
            
            # Patch Tkinter's _tkinter module to prevent menu creation
            try:
                import _tkinter
                def _patched_call(*args, **kwargs):
                    cmd = args[0] if args else ''
                    if isinstance(cmd, str) and ('menu' in cmd.lower() or 'menubar' in cmd.lower()):
                        return None
                    return original_call(*args, **kwargs)
                
                if hasattr(_tkinter, 'TkappType'):
                    if hasattr(_tkinter.TkappType, 'call'):
                        original_call = _tkinter.TkappType.call
                        _tkinter.TkappType.call = _patched_call
            except Exception as e:
                print("Failed to patch Tkinter:", e)
        
        # Additional debug info
        print("Python executable:", sys.executable)
        print("TK_LIBRARY:", os.environ.get('TK_LIBRARY'))
        print("TCL_LIBRARY:", os.environ.get('TCL_LIBRARY'))
        print("TKPATH:", os.environ.get('TKPATH'))
        print("TK_NO_NATIVE_MENUBAR:", os.environ.get('TK_NO_NATIVE_MENUBAR'))

_fix_tkinter()

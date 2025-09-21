from __future__ import annotations

import sys
import os
import logging
from pathlib import Path
from functools import lru_cache
from typing import Dict

APP_NAME = "TorrentDownloader"


def _expand(path: str) -> Path:
    """Expand env vars and user home in a path string to a Path object."""
    assert isinstance(path, str) and path, "path must be a non-empty string"
    return Path(os.path.expandvars(os.path.expanduser(path)))


@lru_cache(maxsize=1)
def get_app_data_dir() -> str:
    """Return platform specific application data directory.

    Windows: %LOCALAPPDATA%/TorrentDownloader (fallback to home if unset)
    macOS:   ~/Library/Application Support/TorrentDownloader
    Linux:   ~/.local/share/TorrentDownloader
    """
    if sys.platform == 'win32':
        base = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
        return str(_expand(base) / APP_NAME)
    if sys.platform == 'darwin':
        return str(_expand('~/Library/Application Support') / APP_NAME)
    return str(_expand('~/.local/share') / APP_NAME)


@lru_cache(maxsize=1)
def get_log_dir() -> str:
    """Return directory for log files (str)."""
    if sys.platform == 'win32':
        return str(Path(get_app_data_dir()) / 'Logs')
    if sys.platform == 'darwin':
        return str(_expand('~/Library/Logs') / APP_NAME)
    return str(Path(get_app_data_dir()) / 'logs')


@lru_cache(maxsize=1)
def get_cache_dir() -> str:
    """Return directory for cache data (str)."""
    if sys.platform == 'win32':
        return str(Path(get_app_data_dir()) / 'Cache')
    if sys.platform == 'darwin':
        return str(_expand('~/Library/Caches') / APP_NAME)
    return str(_expand('~/.cache') / APP_NAME)


def _xdg_download_dir_from_config() -> Path | None:
    """Attempt to parse ~/.config/user-dirs.dirs for XDG_DOWNLOAD_DIR.

    Returns a Path if successful, else None. This mirrors how modern desktop
    environments (GNOME/KDE) configure user folders.
    """
    config_file = _expand('~/.config/user-dirs.dirs')
    if not config_file.is_file():
        return None
    try:
        for line in config_file.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('XDG_DOWNLOAD_DIR'):
                # Format: XDG_DOWNLOAD_DIR="$HOME/Downloads"
                parts = line.split('=')
                if len(parts) != 2:
                    continue
                raw = parts[1].strip().strip('"')
                # Replace $HOME (common) with expanded home
                raw = raw.replace('$HOME', str(Path.home()))
                return _expand(raw)
    except Exception as e:  # pragma: no cover - defensive
        logging.debug("Failed parsing XDG user dirs file: %s", e)
    return None


@lru_cache(maxsize=1)
def get_downloads_dir() -> str:
    """Return preferred downloads directory for the application.

    Strategy:
      * Windows: Query registry for Downloads GUID; fallback to Documents then home.
      * macOS: ~/Downloads/TorrentDownloader
      * Linux: Try $XDG_DOWNLOAD_DIR, then XDG config file, then ~/Downloads.
    Always append the application folder name to avoid cluttering user root.
    """
    if sys.platform == 'win32':
        try:  # Primary attempt: Known Downloads folder GUID
            import winreg  # type: ignore
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            ) as key:
                try:
                    downloads_path = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
                except OSError:
                    downloads_path = winreg.QueryValueEx(key, "Personal")[0]  # Documents
            return str(_expand(downloads_path) / APP_NAME)
        except Exception as e:  # pragma: no cover - environment specific
            logging.warning("Falling back for Windows downloads dir: %s", e)
            return str(_expand('~/Downloads') / APP_NAME)

    if sys.platform == 'darwin':
        return str(_expand('~/Downloads') / APP_NAME)

    # Linux / Unix
    # 1. Environment variable (explicit override)
    env_dir = os.getenv('XDG_DOWNLOAD_DIR')
    if env_dir:
        return str(_expand(env_dir) / APP_NAME)
    # 2. Config file parsing
    cfg = _xdg_download_dir_from_config()
    if cfg:
        return str(cfg / APP_NAME)
    # 3. Fallback to ~/Downloads
    return str(_expand('~/Downloads') / APP_NAME)


@lru_cache(maxsize=1)
def get_fallback_downloads_dir() -> str:
    """Return fallback downloads directory if primary cannot be created.

    For Linux we keep a lowercase 'downloads' to mirror original behavior.
    """
    if sys.platform == 'win32':
        return str(Path(get_app_data_dir()) / 'Downloads')
    if sys.platform == 'darwin':
        return str(Path(get_cache_dir()) / 'Downloads')
    return str(Path(get_cache_dir()) / 'downloads')


def format_size(size_bytes: int | float | str) -> str:
    """Human friendly size formatting (binary multiples, up to TB).

    Accepts int/float/str (best-effort). Negative values are clamped to 0.
    Returns a string with one decimal place and unit among B, KB, MB, GB, TB.
    Existing tests rely on this specific rounding style.
    """
    assert isinstance(size_bytes, (int, float, str)), "size_bytes must be a number or a string"
    try:  # Normalise input
        size = float(size_bytes)
    except Exception:
        size = 0.0
    if size < 0:
        size = 0.0
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def ensure_app_dirs(create_downloads: bool = True) -> Dict[str, str]:
    """Ensure core application directories exist and return their paths.

    Parameters
    ----------
    create_downloads: bool
        Whether to also create the (primary) downloads directory.

    Returns
    -------
    dict mapping of {'app_data','log','cache','downloads?'} to their paths.
    """
    assert isinstance(create_downloads, bool), "create_downloads must be a boolean"
    paths = {
        'app_data': get_app_data_dir(),
        'log': get_log_dir(),
        'cache': get_cache_dir(),
    }
    for key in list(paths.keys()):
        try:
            Path(paths[key]).mkdir(parents=True, exist_ok=True)
        except Exception as e:  # pragma: no cover - filesystem edge
            logging.warning("Failed to create %s directory (%s): %s", key, paths[key], e)
    if create_downloads:
        d = get_downloads_dir()
        try:
            Path(d).mkdir(parents=True, exist_ok=True)
            paths['downloads'] = d
        except Exception as e:  # pragma: no cover
            logging.error("Failed to create downloads dir %s: %s", d, e)
            fb = get_fallback_downloads_dir()
            Path(fb).mkdir(parents=True, exist_ok=True)
            paths['downloads'] = fb
    return paths


__all__ = [
    'get_app_data_dir',
    'get_log_dir',
    'get_cache_dir',
    'get_downloads_dir',
    'get_fallback_downloads_dir',
    'format_size',
    'ensure_app_dirs',
]


"""Torrent session and management logic.

This module isolates all libtorrent specific logic from the GUI layer so the
Tkinter code focuses purely on presentation and user interaction.

Key concepts:
 - TorrentManager: owns a libtorrent session and provides high-level methods
   to add torrents (by magnet URI) and query their status.
 - TorrentStatus: a light-weight dataclass snapshot of a single torrent's
   current state, independent from libtorrent internal objects. The GUI can
   safely consume these without needing to import libtorrent directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol, runtime_checkable
import logging
import os

import libtorrent as lt  # type: ignore


@dataclass
class LoadedTorrentInfo:
    info_hash: str
    magnet_link: Optional[str]


@dataclass
class TorrentStatus:
    name: str
    progress: float  # 0..1
    download_rate: int  # bytes/sec
    upload_rate: int  # bytes/sec
    num_peers: int
    eta_seconds: Optional[int]  # None if not available
    has_metadata: bool
    state: str  # E.g., "downloading", "seeding", "paused"


@runtime_checkable
class _HandleLike(Protocol):  # pragma: no cover - structural typing helper
    """Subset of the libtorrent torrent_handle API we rely on.

    This lets us unit test the translation logic with simple fakes instead of
    requiring real libtorrent sessions (which would make tests slow & flaky).
    """
    def status(self): ...  # noqa: D401,E701,F401
    def has_metadata(self) -> bool: ...  # noqa: D401,E701,F401
    def name(self) -> str: ...  # noqa: D401,E701,F401


def _compute_progress(progress_field: float, total_done: int, total_wanted: int) -> float:
    """Return a sane 0..1 progress value.

    libtorrent exposes both a floating ``progress`` attribute (0..1) and the
    integer counters ``total_done`` & ``total_wanted``. In some circumstances –
    especially directly after adding a torrent file – ``progress`` can report
    an unexpectedly high value (e.g. pieces pre-marked as complete / padding).

    We prefer a recomputed ratio when total_wanted is positive to mitigate
    early jumps. Values are clamped to the [0,1] interval.
    """
    assert isinstance(progress_field, float), "progress_field must be a float"
    assert isinstance(total_done, int), "total_done must be an integer"
    assert isinstance(total_wanted, int), "total_wanted must be an integer"
    if total_wanted > 0:
        ratio = total_done / float(total_wanted)
    else:  # defensive – avoid divide by zero; fall back to provided field
        ratio = progress_field
    # Clamp & normalise
    if ratio < 0:
        ratio = 0.0
    elif ratio > 1:
        ratio = 1.0
    return float(ratio)


def _compute_eta(total_done: int, total_wanted: int, download_rate: int) -> Optional[int]:
    """Estimate remaining seconds or return None if not computable.

    We deliberately avoid huge oscillations: if the download rate is <= 0 or
    remaining bytes are not positive, we return None.
    """
    assert isinstance(total_done, int), "total_done must be an integer"
    assert isinstance(total_wanted, int), "total_wanted must be an integer"
    assert isinstance(download_rate, int), "download_rate must be an integer"
    remaining = total_wanted - total_done
    if download_rate <= 0 or remaining <= 0:
        return None
    # int truncation acts as floor which is fine for an ETA display
    return int(remaining / download_rate)


def _get_state_str(s) -> str:
    """Return a human-readable string for the torrent's state."""
    if not lt:
        return "N/A"
    state_map = {
        lt.torrent_status.states.checking_files: "checking",
        lt.torrent_status.states.downloading_metadata: "metadata",
        lt.torrent_status.states.downloading: "downloading",
        lt.torrent_status.states.finished: "finished",
        lt.torrent_status.states.seeding: "seeding",
        lt.torrent_status.states.allocating: "allocating",
        lt.torrent_status.states.checking_resume_data: "checking resume",
    }
    state = s.state
    if s.paused:
        return "paused"
    return state_map.get(state, str(state))


def _status_from_handle(handle: _HandleLike) -> TorrentStatus:
    """Translate a libtorrent ``torrent_handle`` into a ``TorrentStatus``.

    This function acts as a translation layer between the libtorrent library
    and the application's internal data structure. It isolates the GUI from
    libtorrent-specific details.
    """
    assert isinstance(handle, _HandleLike), "handle must be a _HandleLike object"
    try:
        s = handle.status()
    except Exception as e:  # pragma: no cover - defensive
        logging.warning("Failed to retrieve status for handle: %s", e)
        raise

    # Check if the torrent has metadata. Without it, we can't get the name or file info.
    has_metadata = False
    try:
        has_metadata = handle.has_metadata()
    except Exception:  # pragma: no cover - defensive
        pass

    # If metadata is not yet available, return a placeholder status.
    if not has_metadata:
        return TorrentStatus(
            name="(retrieving metadata)",
            progress=0.0,
            download_rate=0,
            upload_rate=0,
            num_peers=getattr(s, 'num_peers', 0),
            eta_seconds=None,
            has_metadata=False,
            state=_get_state_str(s),
        )

    # Extract status details, using getattr for safety in case of API changes.
    total_wanted = getattr(s, 'total_wanted', 0) or 0
    total_done = getattr(s, 'total_done', 0) or 0
    progress_field = getattr(s, 'progress', 0.0) or 0.0
    download_rate = getattr(s, 'download_rate', 0) or 0
    upload_rate = getattr(s, 'upload_rate', 0) or 0
    num_peers = getattr(s, 'num_peers', 0) or 0

    # Use custom helpers to calculate a more stable progress and ETA.
    progress = _compute_progress(progress_field, total_done, total_wanted)
    eta_seconds = _compute_eta(total_done, total_wanted, download_rate)

    try:
        name = handle.name()
    except Exception:  # pragma: no cover - defensive
        name = "(unknown)"

    # Construct the final status object for the GUI.
    return TorrentStatus(
        name=name,
        progress=progress,
        download_rate=download_rate,
        upload_rate=upload_rate,
        num_peers=num_peers,
        eta_seconds=eta_seconds,
        has_metadata=True,
        state=_get_state_str(s),
    )


class TorrentManager:
    """Encapsulates libtorrent session operations."""

    def __init__(self, download_dir: str, session_file: str):
        """Initialise the torrent session, optionally loading from a saved state."""
        assert isinstance(download_dir, str) and download_dir, "download_dir must be a non-empty string"
        assert isinstance(session_file, str) and session_file, "session_file must be a non-empty string"
        if lt is None:
            raise RuntimeError("libtorrent library not available")
        self._download_dir = download_dir
        self._session_file = session_file
        self._resume_file = session_file + ".resume"

        # Initialise the libtorrent session object.
        self._session = lt.session()
        self._load_session_state()

        # Apply settings for listening ports, DHT, etc.
        settings = {
            'listen_interfaces': '0.0.0.0:6881,[::]:6881',
            'enable_dht': True,
            'enable_lsd': True,
            'enable_upnp': True,
            'enable_natpmp': True,
            'outgoing_interfaces': '',
            'alert_mask': lt.alert.category_t.all_categories,
            'download_rate_limit': 0,  # Unlimited
            'upload_rate_limit': 0,  # Unlimited
        }
        self._session.apply_settings(settings)
        logging.info("Configured libtorrent session with settings: %s", settings)

        # Default parameters for adding new torrents.
        self._params = {
            'save_path': self._download_dir,
            'storage_mode': lt.storage_mode_t(2),  # Use sparse allocation
        }



    def _load_session_state(self):
        """Load session state from file if it exists."""
        self._handles = [] # Clear existing handles before loading
        if os.path.exists(self._session_file):
            try:
                with open(self._session_file, 'rb') as f:
                    data = lt.bdecode(f.read())
                    self._session.load_state(data)
                    logging.info(f"Session state loaded from {self._session_file}")
            except Exception as e:
                logging.error(f"Failed to load session state: {e}")

        if os.path.exists(self._resume_file):
            try:
                with open(self._resume_file, 'rb') as f:
                    resume_data_list = lt.bdecode(f.read())
                
                for resume_data in resume_data_list:
                    atp = lt.read_resume_data(resume_data)
                    atp.save_path = self._download_dir # Ensure correct save path
                    handle = self._session.add_torrent(atp)
                    self._handles.append(handle)
                logging.info(f"Loaded resume data for {len(resume_data_list)} torrents from {self._resume_file}")
            except Exception as e:
                logging.error(f"Failed to load resume data: {e}")

    def save_state(self):
        """Save the current session state to a file."""
        try:
            # Save session state
            with open(self._session_file, 'wb') as f:
                f.write(lt.bencode(self._session.save_state()))
            logging.info(f"Session state saved to {self._session_file}")

            # Save resume data for all torrents
            resume_data = []
            # Request resume data for all torrents
            self._session.post_torrent_updates() # Ensure all torrents are up-to-date
            self._session.post_dht_stats() # Ensure DHT stats are up-to-date
            self._session.post_session_stats() # Ensure session stats are up-to-date

            for h in self._handles:
                if h.is_valid():
                    h.save_resume_data()

            # Wait for resume data alerts
            alerts = []
            self._session.wait_for_alert(1000) # Wait for up to 1 second for alerts
            alerts = self._session.pop_alerts()

            for a in alerts:
                if isinstance(a, lt.save_resume_data_alert):
                    resume_data.append(a.resume_data)
            
            if resume_data:
                with open(self._resume_file, 'wb') as f:
                    f.write(lt.bencode(resume_data))
                logging.info(f"Resume data for {len(resume_data)} torrents saved to {self._resume_file}")

        except Exception as e:
            logging.error(f"Failed to save session or resume data: {e}")

    def add_magnet(self, magnet_uri: str):
        """Add a magnet URI to the session and track its handle."""
        assert isinstance(magnet_uri, str) and magnet_uri.startswith("magnet:?"), "magnet_uri must be a valid magnet link"
        # lt.add_magnet_uri() is asynchronous, it returns a handle immediately.
        handle = self._session.add_magnet_uri(magnet_uri, self._params)
        self._handles.append(handle)
        logging.debug("Added magnet URI: %s", magnet_uri)
        return handle

    def add_torrent_file(self, torrent_path: str):
        """Add a .torrent file to the session."""
        assert isinstance(torrent_path, str) and torrent_path, "torrent_path must be a non-empty string"
        if not os.path.isfile(torrent_path):
            raise FileNotFoundError(f"Torrent file not found: {torrent_path}")
        # Load the .torrent file to get its metadata.
        try:
            info = lt.torrent_info(torrent_path)
        except Exception as e:  # pragma: no cover - libtorrent internal errors
            raise RuntimeError(f"Failed to parse torrent file: {e}") from e

        params = dict(self._params)  # shallow copy
        params['ti'] = info
        # Add the torrent to the session.
        try:
            handle = self._session.add_torrent(params)
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Failed to add torrent: {e}") from e

        self._handles.append(handle)
        logging.debug("Added torrent file: %s", torrent_path)
        return handle

    def set_download_directory(self, path: str):
        """Sets the download directory for new torrents."""
        assert isinstance(path, str) and path, "path must be a non-empty string"
        self._download_dir = path
        self._params['save_path'] = path

    def get_torrents(self) -> List:
        """Return the list of torrent handles."""
        return self._handles

    def get_loaded_torrents_info(self) -> List[LoadedTorrentInfo]:
        """Return info about torrents loaded from the session state."""
        info_list = []
        for handle in self._handles:
            if not handle.is_valid():
                continue
            info_hash = str(handle.info_hash())
            magnet_link = None
            try:
                # This can fail for torrents added from files
                magnet_link = lt.make_magnet_uri(handle)
            except Exception:
                pass
            info_list.append(LoadedTorrentInfo(info_hash=info_hash, magnet_link=magnet_link))
        return info_list

    def pause_at(self, index: int) -> bool:
        """Pause torrent at a given index."""
        assert isinstance(index, int), "index must be an integer"
        if index < 0 or index >= len(self._handles):
            return False
        handle = self._handles[index]
        # Check if the torrent is valid and can be paused.
        if handle.is_valid() and handle.status().pausable:
            handle.pause()
            return True
        return False

    def resume_at(self, index: int) -> bool:
        """Resume torrent at a given index."""
        assert isinstance(index, int), "index must be an integer"
        if index < 0 or index >= len(self._handles):
            return False
        handle = self._handles[index]
        # Check if the torrent is valid and is currently paused.
        if handle.is_valid() and handle.status().paused:
            handle.resume()
            return True
        return False

    def get_status_list(self) -> List[TorrentStatus]:
        """Return a list of status objects for all torrents."""
        statuses: List[TorrentStatus] = []
        for handle in list(self._handles):
            try:
                statuses.append(_status_from_handle(handle))
            except Exception:  # pragma: no cover - already logged in helper
                continue
        return statuses

    def remove_at(self, index: int, *, delete_files: bool = False) -> bool:
        """Remove torrent at given index, optionally deleting its files."""
        assert isinstance(index, int), "index must be an integer"
        assert isinstance(delete_files, bool), "delete_files must be a boolean"
        if index < 0 or index >= len(self._handles):
            return False
        try:
            # Remove the handle from our internal list.
            handle = self._handles.pop(index)
            # Remove the torrent from the libtorrent session.
            if delete_files:
                # Use the delete_files flag to remove data from disk.
                self._session.remove_torrent(handle, lt.options_t.delete_files)
            else:
                self._session.remove_torrent(handle)
            logging.info("Removed torrent at index %s (delete_files=%s)", index, delete_files)
            return True
        except Exception as e:  # pragma: no cover - defensive
            # Guard against errors if the handle is no longer valid.
            logging.error("Failed to remove torrent at index %s: %s", index, e)
            return False

    @property
    def download_dir(self) -> str:
        return self._download_dir

__all__ = [
    "TorrentManager",
    "TorrentStatus",
    # Helper exports (documented for testing & potential reuse)
    "_compute_progress",
    "_compute_eta",
    "_status_from_handle",
]
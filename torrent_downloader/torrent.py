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

try:
	import libtorrent as lt  # type: ignore
except ImportError as e:  # pragma: no cover - handled at startup
	logging.error("Failed to import libtorrent in torrent module: %s", e)
	lt = None  # type: ignore


@dataclass
class TorrentStatus:
	name: str
	progress: float  # 0..1
	download_rate: int  # bytes/sec
	upload_rate: int  # bytes/sec
	num_peers: int
	eta_seconds: Optional[int]  # None if not available
	has_metadata: bool


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
	remaining = total_wanted - total_done
	if download_rate <= 0 or remaining <= 0:
		return None
	# int truncation acts as floor which is fine for an ETA display
	return int(remaining / download_rate)


def _status_from_handle(handle: _HandleLike) -> TorrentStatus:
	"""Translate a libtorrent ``torrent_handle`` into a ``TorrentStatus``.

	Isolated for unit testing with simple fake objects.
	"""
	try:
		s = handle.status()
	except Exception as e:  # pragma: no cover - defensive
		logging.warning("Failed to retrieve status for handle: %s", e)
		raise

	has_metadata = False
	try:
		has_metadata = handle.has_metadata()
	except Exception:  # pragma: no cover - defensive
		pass

	if not has_metadata:
		return TorrentStatus(
			name="(retrieving metadata)",
			progress=0.0,
			download_rate=0,
			upload_rate=0,
			num_peers=getattr(s, 'num_peers', 0),
			eta_seconds=None,
			has_metadata=False,
		)

	# Safe attribute access with defaults (defensive if libtorrent changes)
	total_wanted = getattr(s, 'total_wanted', 0) or 0
	total_done = getattr(s, 'total_done', 0) or 0
	progress_field = getattr(s, 'progress', 0.0) or 0.0
	download_rate = getattr(s, 'download_rate', 0) or 0
	upload_rate = getattr(s, 'upload_rate', 0) or 0
	num_peers = getattr(s, 'num_peers', 0) or 0

	progress = _compute_progress(progress_field, total_done, total_wanted)
	eta_seconds = _compute_eta(total_done, total_wanted, download_rate)

	try:
		name = handle.name()
	except Exception:  # pragma: no cover - defensive
		name = "(unknown)"

	return TorrentStatus(
		name=name,
		progress=progress,
		download_rate=download_rate,
		upload_rate=upload_rate,
		num_peers=num_peers,
		eta_seconds=eta_seconds,
		has_metadata=True,
	)


class TorrentManager:
	"""Encapsulates libtorrent session operations."""

	def __init__(self, download_dir: str):
		if lt is None:
			raise RuntimeError("libtorrent library not available")
		self._download_dir = download_dir
		self._session = lt.session()
		settings = {
			'listen_interfaces': '0.0.0.0:6881,[::]:6881',
			'enable_dht': True,
			'enable_lsd': True,
			'enable_upnp': True,
			'enable_natpmp': True,
			'outgoing_interfaces': '',
			'alert_mask': lt.alert.category_t.all_categories,
			'download_rate_limit': 0,
			'upload_rate_limit': 0,
		}
		self._session.apply_settings(settings)
		logging.info("Configured libtorrent session with settings: %s", settings)

		self._params = {
			'save_path': self._download_dir,
			'storage_mode': lt.storage_mode_t(2),  # sparse
		}
		self._handles: List = []

	def add_magnet(self, magnet_uri: str):
		"""Add a magnet URI to the session and track its handle."""
		handle = lt.add_magnet_uri(self._session, magnet_uri, self._params)
		self._handles.append(handle)
		logging.debug("Added magnet URI: %s", magnet_uri)
		return handle

	def add_torrent_file(self, torrent_path: str):
		"""Add a .torrent file to the session.

		Returns the torrent handle. Raises FileNotFoundError if the path does not
		exist or RuntimeError if libtorrent fails to load the file.
		"""
		if not os.path.isfile(torrent_path):
			raise FileNotFoundError(f"Torrent file not found: {torrent_path}")
		try:
			info = lt.torrent_info(torrent_path)
		except Exception as e:  # pragma: no cover - libtorrent internal errors
			raise RuntimeError(f"Failed to parse torrent file: {e}") from e

		params = dict(self._params)  # shallow copy
		params['ti'] = info
		try:
			handle = self._session.add_torrent(params)
		except Exception as e:  # pragma: no cover
			raise RuntimeError(f"Failed to add torrent: {e}") from e

		self._handles.append(handle)
		logging.debug("Added torrent file: %s", torrent_path)
		return handle

	def get_status_list(self) -> List[TorrentStatus]:
		statuses: List[TorrentStatus] = []
		for handle in list(self._handles):
			try:
				statuses.append(_status_from_handle(handle))
			except Exception:  # pragma: no cover - already logged in helper
				continue
		return statuses

	def remove_at(self, index: int, *, delete_files: bool = False) -> bool:
		"""Remove torrent at given index.

		If ``delete_files`` is False (default) the downloaded data is kept on disk –
		we only stop / remove the torrent from the session. Returns True if a
		torrent was removed, False if index invalid.
		"""
		if index < 0 or index >= len(self._handles):
			return False
		try:
			handle = self._handles.pop(index)
			if delete_files:
				# Guard for older libtorrent versions lacking options_t
				try:
					self._session.remove_torrent(handle, lt.options_t.delete_files)  # type: ignore[attr-defined]
				except Exception:
					self._session.remove_torrent(handle)
			else:
				self._session.remove_torrent(handle)
			logging.info("Removed torrent at index %s (delete_files=%s)", index, delete_files)
			return True
		except Exception as e:  # pragma: no cover - defensive
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

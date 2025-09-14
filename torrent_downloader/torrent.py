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
from typing import List, Optional
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
				s = handle.status()
			except Exception as e:  # pragma: no cover - defensive
				logging.warning("Failed to retrieve status for handle: %s", e)
				continue

			has_metadata = handle.has_metadata()
			if not has_metadata:
				statuses.append(TorrentStatus(
					name="(retrieving metadata)",
					progress=0.0,
					download_rate=0,
					upload_rate=0,
					num_peers=s.num_peers,
					eta_seconds=None,
					has_metadata=False,
				))
				continue

			remaining_bytes = s.total_wanted - s.total_done
			eta_seconds = None
			if s.download_rate > 0 and remaining_bytes > 0:
				eta_seconds = int(remaining_bytes / s.download_rate)

			try:
				name = handle.name()
			except Exception:  # pragma: no cover
				name = "(unknown)"

			statuses.append(TorrentStatus(
				name=name,
				progress=s.progress,  # already 0..1
				download_rate=s.download_rate,
				upload_rate=s.upload_rate,
				num_peers=s.num_peers,
				eta_seconds=eta_seconds,
				has_metadata=True,
			))
		return statuses

	@property
	def download_dir(self) -> str:
		return self._download_dir

__all__ = ["TorrentManager", "TorrentStatus"]

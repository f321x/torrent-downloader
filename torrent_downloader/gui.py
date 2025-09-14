from tkinter import messagebox, ttk, filedialog
import tkinter as tk
import logging
import sys
import os
import subprocess
from typing import List, Sequence, Tuple, Optional

try:  # Early feedback if libtorrent missing – GUI exits cleanly
    import libtorrent  # noqa: F401
except ImportError as e:  # pragma: no cover - startup failure path
    logging.error("Failed to import libtorrent: %s", e)
    print('Error: libtorrent module not found. Install with: pip install python-libtorrent')
    sys.exit(1)

from . import util
from .torrent import TorrentManager, TorrentStatus

POLL_INTERVAL_MS = 1000
MAX_NAME_LEN = 50


class TorrentDownloaderApp:

    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Torrent Downloader")
        master.geometry("1000x600")
        master.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Internal state
        self._magnets: set[str] = set()
        self._info_hashes: set[str] = set()  # track torrents added via file
        self._update_job: Optional[str] = None
        self._last_rows: List[Tuple[str, str, str, str, str]] = []

        # Create a custom toolbar frame
        self.toolbar = ttk.Frame(master)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Add toolbar buttons
        self.open_folder_button = ttk.Button(self.toolbar, text="Open Downloads",
                                             command=self.open_download_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_torrent_file_button = ttk.Button(self.toolbar, text="Add Torrent File", command=self.add_torrent_file_dialog)
        self.add_torrent_file_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.help_button = ttk.Button(self.toolbar, text="Help", command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.quit_button = ttk.Button(self.toolbar, text="Quit", command=self.quit_app)
        self.quit_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', background='#f0f0f0')

        # Main container
        self.main_container = ttk.Frame(master, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Top frame for magnet link entry
        self.frame_top = ttk.Frame(self.main_container)
        self.frame_top.pack(fill=tk.X, pady=(0, 10))

        self.label = ttk.Label(self.frame_top, text="Magnet Link:")
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        self.magnet_entry = ttk.Entry(self.frame_top)
        self.magnet_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.magnet_entry.bind("<Return>", lambda _e: self.add_magnet())
        self.magnet_entry.focus_set()

        self.add_button = ttk.Button(self.frame_top, text="Add Magnet", command=self.add_magnet)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # Status frame with Treeview
        self.frame_status = ttk.Frame(self.main_container)
        self.frame_status.pack(fill=tk.BOTH, expand=True)

        # Create Treeview
        self.tree = ttk.Treeview(self.frame_status,
                                 columns=("name", "progress", "speed", "eta", "peers"),
                                 show="headings")

        # Define column headings and widths
        self.tree.heading("name", text="Name")
        self.tree.heading("progress", text="Progress")
        self.tree.heading("speed", text="Speed")
        self.tree.heading("eta", text="ETA")
        self.tree.heading("peers", text="Peers")

        # Set column widths
        self.tree.column("name", width=400, minwidth=200)
        self.tree.column("progress", width=100, minwidth=80)
        self.tree.column("speed", width=200, minwidth=150)
        self.tree.column("eta", width=100, minwidth=80)
        self.tree.column("peers", width=80, minwidth=60)

        # Add scrollbars
        vsb = ttk.Scrollbar(self.frame_status, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Grid layout
        self.tree.grid(column=0, row=0, sticky="nsew")
        vsb.grid(column=1, row=0, sticky="ns")

        # Configure grid weights
        self.frame_status.grid_columnconfigure(0, weight=1)
        self.frame_status.grid_rowconfigure(0, weight=1)

        # Prepare download directory and torrent manager
        self.download_dir = self._resolve_download_dir()
        self.manager = TorrentManager(self.download_dir)
        self.download_location_text = f"Downloads folder: {self.download_dir}"
        self._schedule_update()

    def show_help(self):
        help_text = f"""
Torrent Downloader Help

Add by Magnet Link:
    1. Paste a magnet link in the text field
    2. Click 'Add Magnet' (or press Enter)

Add by .torrent File:
    1. Click 'Add Torrent File'
    2. Choose a .torrent file from your system

General:
    - Progress, speeds and peers update every {POLL_INTERVAL_MS/1000:.0f}s
    - Duplicate magnets or torrent files (same info hash) are ignored

{self.download_location_text}

For support, please visit:
https://github.com/yourusername/torrent_downloader
"""
        messagebox.showinfo("Help", help_text)

    def open_download_folder(self):
        """Open the downloads folder in the system file explorer."""
        try:
            if sys.platform == 'win32':  # type: ignore[attr-defined]
                os.startfile(self.download_dir)  # noqa: PLW1510
            elif sys.platform == 'darwin':
                subprocess.Popen(["open", self.download_dir])
            else:
                subprocess.Popen(["xdg-open", self.download_dir])
        except Exception as e:  # pragma: no cover - platform dependent
            logging.error("Failed to open downloads folder: %s", e)
            messagebox.showerror("Error", f"Could not open downloads folder:\n{e}")

    def add_magnet(self):
        magnet_link = self.magnet_entry.get().strip()
        if not magnet_link:
            return
        if not magnet_link.startswith("magnet:?"):
            messagebox.showwarning("Invalid Magnet", "Magnet link should start with 'magnet:?'")
            return
        if magnet_link in self._magnets:
            messagebox.showinfo("Duplicate", "This magnet link was already added.")
            return
        try:
            self.manager.add_magnet(magnet_link)
            self._magnets.add(magnet_link)
            self.magnet_entry.delete(0, tk.END)
        except Exception as e:  # pragma: no cover - libtorrent edge
            logging.error("Failed to add magnet: %s", e)
            messagebox.showerror("Error", f"Failed to add magnet: {e}")

    def add_torrent_file_dialog(self):
        filename = filedialog.askopenfilename(
            title="Select .torrent file",
            filetypes=[("Torrent files", "*.torrent"), ("All files", "*")],
        )
        if not filename:
            return
        try:
            # Peek at info hash to detect duplicates before adding
            import libtorrent as lt  # local import to ensure availability
            try:
                info = lt.torrent_info(filename)
            except Exception as e:  # pragma: no cover - parsing edge
                messagebox.showerror("Error", f"Failed to read torrent file: {e}")
                return
            info_hash = str(info.info_hash()) if hasattr(info, 'info_hash') else str(info.info_hashes().v1)
            if info_hash in self._info_hashes:
                messagebox.showinfo("Duplicate", "This torrent file (info hash) was already added.")
                return
            # Add through manager (recreates torrent_info internally but ok for simplicity)
            self.manager.add_torrent_file(filename)
            self._info_hashes.add(info_hash)
        except FileNotFoundError:
            messagebox.showerror("Error", "Torrent file not found.")
        except Exception as e:  # pragma: no cover - defensive
            logging.error("Failed to add torrent file: %s", e)
            messagebox.showerror("Error", f"Failed to add torrent file: {e}")

    def quit_app(self):
        if self._update_job is not None:
            try:
                self.master.after_cancel(self._update_job)
            except Exception:  # pragma: no cover - defensive
                pass
            self._update_job = None
        self.master.destroy()

    # Removed local format_size; use util.format_size

    def _resolve_download_dir(self) -> str:
        """Determine and create downloads directory with fallback strategy."""
        download_dir = util.get_downloads_dir()
        try:
            os.makedirs(download_dir, exist_ok=True)
            logging.info(f"Using download directory: {download_dir}")
            return download_dir
        except OSError as e:
            logging.error(f"Failed to create downloads directory: {e}")
            fallback = util.get_fallback_downloads_dir()
            os.makedirs(fallback, exist_ok=True)
            logging.info(f"Using fallback download directory: {fallback}")
            return fallback

    # --- Internal helpers -------------------------------------------------
    def _schedule_update(self):
        self._update_job = self.master.after(POLL_INTERVAL_MS, self.update_status)

    @staticmethod
    def _format_eta(seconds: Optional[int]) -> str:
        if seconds is None:
            return "N/A"
        m, sec = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{sec:02d}"

    @staticmethod
    def _shorten(name: str, max_len: int = MAX_NAME_LEN) -> str:
        return name if len(name) <= max_len else name[: max_len - 3] + "..."

    def _build_rows(self, statuses: Sequence[TorrentStatus]) -> List[Tuple[str, str, str, str, str]]:
        if not statuses:
            return [("No active torrents", "", "", "", "")]
        rows: List[Tuple[str, str, str, str, str]] = []
        for st in statuses:
            if not st.has_metadata:
                rows.append(("Downloading metadata...", "N/A", "N/A", "N/A", str(st.num_peers)))
                continue
            progress = f"{st.progress * 100:.1f}%"
            d_rate = util.format_size(st.download_rate)
            u_rate = util.format_size(st.upload_rate)
            speed = f"↓{d_rate}/s ↑{u_rate}/s"
            eta_str = self._format_eta(st.eta_seconds)
            rows.append((self._shorten(st.name), progress, speed, eta_str, str(st.num_peers)))
        return rows

    def _refresh_tree(self, rows: Sequence[Tuple[str, str, str, str, str]]):
        # Only update if rows changed to reduce flicker / overhead
        if list(rows) == self._last_rows:
            return
        # Full rebuild (simpler and still cheap for small list)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=r)
        self._last_rows = list(rows)

    def update_status(self):
        try:
            statuses: List[TorrentStatus] = self.manager.get_status_list()
            rows = self._build_rows(statuses)
            self._refresh_tree(rows)
        except Exception as e:  # pragma: no cover - UI defensive
            logging.error("Error updating status: %s", e)
        finally:
            # Reschedule only if window still exists
            if self.master.winfo_exists():
                self._schedule_update()

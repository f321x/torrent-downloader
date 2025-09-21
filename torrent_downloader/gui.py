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
        self._last_rows: List[Tuple[str, str, str, str, str, str]] = []

        # Create a custom toolbar frame
        self.toolbar = ttk.Frame(master)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Add toolbar buttons
        self.open_folder_button = ttk.Button(self.toolbar, text="Open Downloads",
                                             command=self.open_download_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Unified add torrent button (magnet or file)
        self.add_torrent_button = ttk.Button(self.toolbar, text="Add Torrent", command=self.open_add_dialog)
        self.add_torrent_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Remove selected torrents button
        self.remove_button = ttk.Button(self.toolbar, text="Remove Selected", command=self.remove_selected)
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.resume_button = ttk.Button(self.toolbar, text="Resume Selected", command=self.resume_selected)
        self.resume_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = ttk.Button(self.toolbar, text="Pause Selected", command=self.pause_selected)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

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

        # Space at top before tree (former magnet input area)
        spacer = ttk.Frame(self.main_container, height=5)
        spacer.pack(fill=tk.X)

        # Status frame with Treeview
        self.frame_status = ttk.Frame(self.main_container)
        self.frame_status.pack(fill=tk.BOTH, expand=True)

        # Create Treeview
        self.tree = ttk.Treeview(self.frame_status,
                                 columns=("name", "progress", "speed", "eta", "peers", "state"),
                                 show="headings")

        # Define column headings and widths
        self.tree.heading("name", text="Name")
        self.tree.heading("progress", text="Progress")
        self.tree.heading("speed", text="Speed")
        self.tree.heading("eta", text="ETA")
        self.tree.heading("peers", text="Peers")
        self.tree.heading("state", text="State")

        # Set column widths
        self.tree.column("name", width=400, minwidth=200)
        self.tree.column("progress", width=100, minwidth=80)
        self.tree.column("speed", width=200, minwidth=150)
        self.tree.column("eta", width=100, minwidth=80)
        self.tree.column("peers", width=80, minwidth=60)
        self.tree.column("state", width=100, minwidth=80)

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
        session_file = os.path.join(util.get_cache_dir(), "session.dat")
        self.manager = TorrentManager(self.download_dir, session_file)
        self.download_location_text = f"Downloads folder: {self.download_dir}"
        self._schedule_update()
        # Key bindings for removal (Delete / Shift+Delete for delete files)
        self.tree.bind('<Delete>', lambda e: self.remove_selected(delete_files=bool(e.state & 0x0001)))
        # Also allow BackSpace as alternate delete key
        self.tree.bind('<BackSpace>', lambda _e: self.remove_selected())

        # Context menu
        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label="Resume", command=self.resume_selected)
        self.context_menu.add_command(label="Pause", command=self.pause_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove", command=self.remove_selected)
        self.context_menu.add_command(label="Remove and Delete Data", command=lambda: self.remove_selected(delete_files=True))
        self.tree.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        """Display the context menu at the cursor position."""
        # Identify the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            # Select the item under the cursor if it's not already selected
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)



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

    # --- Unified add dialog -------------------------------------------------
    def open_add_dialog(self):
        """Open a simple dialog to enter a magnet OR pick a .torrent file.
        If both are supplied the most recently edited wins and the other is cleared.
        """
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Torrent")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.resizable(False, False)

        magnet_var = tk.StringVar()
        file_var = tk.StringVar()

        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Magnet Link:").pack(anchor=tk.W)
        magnet_entry = ttk.Entry(frame, textvariable=magnet_var, width=70)
        magnet_entry.pack(fill=tk.X, pady=(0, 8))
        magnet_entry.focus_set()

        ttk.Label(frame, text="Torrent File:").pack(anchor=tk.W)
        file_row = ttk.Frame(frame)
        file_row.pack(fill=tk.X)
        file_entry = ttk.Entry(file_row, textvariable=file_var, width=55)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def browse():
            filename = filedialog.askopenfilename(
                title="Select .torrent file",
                filetypes=[("Torrent files", "*.torrent"), ("All files", "*")],
            )
            if filename:
                file_var.set(filename)
                # Clear magnet if a file picked
                if magnet_var.get():
                    magnet_var.set("")

        ttk.Button(file_row, text="Browse", command=browse).pack(side=tk.LEFT, padx=(5, 0))

        # Mutual exclusion handlers
        def on_magnet_change(*_):
            if magnet_var.get():
                file_var.set("")

        magnet_var.trace_add('write', on_magnet_change)

        # Action buttons
        btn_frame = ttk.Frame(dialog, padding=(0, 5, 0, 10))
        btn_frame.pack(fill=tk.X)

        def do_add():
            magnet = magnet_var.get().strip()
            file_path = file_var.get().strip()
            if magnet and file_path:
                # Defensive: choose magnet (user typed after selecting file)
                file_var.set("")
                file_path = ""
            if not magnet and not file_path:
                messagebox.showwarning("Nothing to Add", "Provide a magnet link or choose a .torrent file.")
                return
            if magnet:
                self._add_magnet_link(magnet, parent=dialog)
            else:
                self._add_torrent_file_from_path(file_path, parent=dialog)

        ttk.Button(btn_frame, text="Add", command=do_add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

        dialog.bind('<Return>', lambda _e: do_add())

    def _add_magnet_link(self, magnet_link: str, parent: Optional[tk.Toplevel] = None):
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
            if parent:
                parent.destroy()
        except Exception as e:  # pragma: no cover - libtorrent edge
            logging.error("Failed to add magnet: %s", e)
            messagebox.showerror("Error", f"Failed to add magnet: {e}")

    def _add_torrent_file_from_path(self, filename: str, parent: Optional[tk.Toplevel] = None):
        if not filename:
            return
        try:
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
            self.manager.add_torrent_file(filename)
            self._info_hashes.add(info_hash)
            if parent:
                parent.destroy()
        except FileNotFoundError:
            messagebox.showerror("Error", "Torrent file not found.")
        except Exception as e:  # pragma: no cover - defensive
            logging.error("Failed to add torrent file: %s", e)
            messagebox.showerror("Error", f"Failed to add torrent file: {e}")

    def quit_app(self):
        self.manager.save_state()
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

    def _build_rows(self, statuses: Sequence[TorrentStatus]) -> List[Tuple[str, str, str, str, str, str]]:
        if not statuses:
            return [("No active torrents", "", "", "", "", "")]
        rows: List[Tuple[str, str, str, str, str, str]] = []
        for st in statuses:
            if not st.has_metadata:
                rows.append(("Downloading metadata...", "N/A", "N/A", "N/A", str(st.num_peers), st.state))
                continue
            progress = f"{st.progress * 100:.1f}%"
            d_rate = util.format_size(st.download_rate)
            u_rate = util.format_size(st.upload_rate)
            speed = f"↓{d_rate}/s ↑{u_rate}/s"
            eta_str = self._format_eta(st.eta_seconds)
            rows.append((self._shorten(st.name), progress, speed, eta_str, str(st.num_peers), st.state))
        return rows

    def _refresh_tree(self, rows: Sequence[Tuple[str, str, str, str, str, str]]):
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

    def pause_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        indices = []
        children_order = list(self.tree.get_children())
        for i, item in enumerate(children_order):
            if item in selection:
                indices.append(i)
        if not indices:
            return
        for idx in indices:
            self.manager.pause_at(idx)

    def resume_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        indices = []
        children_order = list(self.tree.get_children())
        for i, item in enumerate(children_order):
            if item in selection:
                indices.append(i)
        if not indices:
            return
        for idx in indices:
            self.manager.resume_at(idx)

    # --- Removal logic ----------------------------------------------------
    def remove_selected(self, delete_files: bool = False):
        """Remove currently selected torrents.

        The tree rows map 1:1 to internal torrent handle list order except the
        placeholder row shown when there are no torrents. We use stored last
        rows to identify indices. Confirmation is requested once for batch.
        """
        selection = self.tree.selection()
        if not selection:
            return
        # If placeholder row present, ignore
        if self._last_rows and self._last_rows[0][0] == "No active torrents":
            return
        # Build indices corresponding to current ordering
        indices = []
        children_order = list(self.tree.get_children())
        for i, item in enumerate(children_order):
            if item in selection:
                indices.append(i)
        if not indices:
            return
        indices.sort(reverse=True)  # remove from end to keep earlier indices stable

        # Ask for confirmation
        if len(indices) == 1:
            msg = "Remove selected torrent?"
        else:
            msg = f"Remove {len(indices)} torrents?"
        if delete_files:
            msg += "\nDelete downloaded data as well?"
        # Provide a simple yes/no; advanced checkbox path skipped for simplicity
        if not messagebox.askyesno("Confirm Removal", msg):
            return
        removed_any = False
        for idx in indices:
            if self.manager.remove_at(idx, delete_files=delete_files):
                removed_any = True
        if removed_any:
            # Invalidate last rows forcing refresh next poll
            self._last_rows = []
            # Immediate UI refresh
            try:
                statuses: List[TorrentStatus] = self.manager.get_status_list()
                rows = self._build_rows(statuses)
                self._refresh_tree(rows)
            except Exception as e:  # pragma: no cover
                logging.error("Failed immediate refresh after removal: %s", e)

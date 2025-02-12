import { create } from 'zustand';
import { TorrentStatus, TorrentSettings, AddTorrentOptions } from '../types/torrent';

interface TorrentStore {
  // State
  torrents: Map<string, TorrentStatus>;
  settings: TorrentSettings;
  isInitialized: boolean;
  error: string | null;

  // Actions
  addTorrent: (options: AddTorrentOptions) => Promise<void>;
  removeTorrent: (id: string, deleteFiles?: boolean) => Promise<void>;
  pauseTorrent: (id: string) => Promise<void>;
  resumeTorrent: (id: string) => Promise<void>;
  updateSettings: (settings: Partial<TorrentSettings>) => Promise<void>;
  initialize: () => Promise<void>;
  updateTorrentStatus: (id: string, status: Partial<TorrentStatus>) => void;
}

const defaultSettings: TorrentSettings = {
  downloadPath: '',  // Will be set by the backend
  maxDownloadSpeed: 0,  // 0 means unlimited
  maxUploadSpeed: 0,
  maxConnections: 200,
  startPaused: false,
};

export const useTorrentStore = create<TorrentStore>((set, get) => ({
  // Initial state
  torrents: new Map(),
  settings: defaultSettings,
  isInitialized: false,
  error: null,

  // Actions
  addTorrent: async (options) => {
    try {
      // TODO: Call Tauri backend to add torrent
      // const response = await invoke('add_torrent', { options });
      // set(state => ({
      //   torrents: new Map(state.torrents).set(response.id, response.status)
      // }));
    } catch (error) {
      set({ error: `Failed to add torrent: ${error}` });
    }
  },

  removeTorrent: async (id, deleteFiles = false) => {
    try {
      // TODO: Call Tauri backend to remove torrent
      // await invoke('remove_torrent', { id, deleteFiles });
      set(state => {
        const newTorrents = new Map(state.torrents);
        newTorrents.delete(id);
        return { torrents: newTorrents };
      });
    } catch (error) {
      set({ error: `Failed to remove torrent: ${error}` });
    }
  },

  pauseTorrent: async (id) => {
    try {
      // TODO: Call Tauri backend to pause torrent
      // await invoke('pause_torrent', { id });
      // Status update will come through the event listener
    } catch (error) {
      set({ error: `Failed to pause torrent: ${error}` });
    }
  },

  resumeTorrent: async (id) => {
    try {
      // TODO: Call Tauri backend to resume torrent
      // await invoke('resume_torrent', { id });
      // Status update will come through the event listener
    } catch (error) {
      set({ error: `Failed to resume torrent: ${error}` });
    }
  },

  updateSettings: async (newSettings) => {
    try {
      // TODO: Call Tauri backend to update settings
      // await invoke('update_settings', { settings: newSettings });
      set(state => ({
        settings: { ...state.settings, ...newSettings }
      }));
    } catch (error) {
      set({ error: `Failed to update settings: ${error}` });
    }
  },

  initialize: async () => {
    try {
      // TODO: Call Tauri backend to get initial state
      // const initialState = await invoke('get_initial_state');
      // set({
      //   settings: initialState.settings,
      //   torrents: new Map(initialState.torrents),
      //   isInitialized: true,
      //   error: null
      // });
    } catch (error) {
      set({ error: `Failed to initialize: ${error}` });
    }
  },

  updateTorrentStatus: (id, status) => {
    set(state => {
      const torrent = state.torrents.get(id);
      if (!torrent) return state;

      const newTorrents = new Map(state.torrents);
      newTorrents.set(id, { ...torrent, ...status });
      return { torrents: newTorrents };
    });
  },
})); 
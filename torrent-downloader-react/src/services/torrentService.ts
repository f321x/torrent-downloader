// The backend will always run locally
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface TorrentInfo {
  id: string;
  name: string;
  progress: number;
  download_speed: number;
  state: string;
  total_size: number;
  downloaded: number;
}

export const torrentService = {
  async addTorrent(magnetLink: string): Promise<{ id: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/torrent/add`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ magnet_link: magnetLink }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add torrent');
    }

    return response.json();
  },

  async listTorrents(): Promise<TorrentInfo[]> {
    const response = await fetch(`${API_BASE_URL}/torrent/list`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch torrents');
    }

    return response.json();
  },

  async removeTorrent(id: string, deleteFiles: boolean = false): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/torrent/${id}?delete_files=${deleteFiles}`,
      { method: 'DELETE' }
    );

    if (!response.ok) {
      throw new Error('Failed to remove torrent');
    }
  },

  async getDownloadsPath(): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/downloads/path`);
    
    if (!response.ok) {
      throw new Error('Failed to get downloads path');
    }

    const data = await response.json();
    return data.path;
  },

  async openDownloadsFolder(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/downloads/open`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to open downloads folder');
    }
  },
}; 
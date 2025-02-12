import WebTorrent from 'webtorrent';

export interface TorrentData {
  infoHash: string;
  name: string;
  progress: number;
  downloadSpeed: number;
  uploadSpeed: number;
  numPeers: number;
  timeRemaining: number;
  size: number;
  downloaded: number;
  status: TorrentStatus;
  error?: string;
}

export type TorrentStatus = 'downloading' | 'seeding' | 'paused' | 'error' | 'complete';

export interface TorrentState {
  torrents: Record<string, TorrentData>;
  client: WebTorrent.Instance | null;
}

export interface AddTorrentOptions {
  magnetUri: string;
} 
export interface TorrentStatus {
  name: string;
  progress: number;
  downloadSpeed: number;
  uploadSpeed: number;
  peers: number;
  state: TorrentState;
  totalSize: number;
  downloadedSize: number;
  remainingTime: number;
  savePath: string;
  error?: string;
}

export enum TorrentState {
  Checking = 'checking',
  Downloading = 'downloading',
  Seeding = 'seeding',
  Paused = 'paused',
  Error = 'error',
  MetadataDownloading = 'metadata_downloading',
  Stopped = 'stopped'
}

export interface AddTorrentOptions {
  magnetUri: string;
  savePath?: string;
  downloadLimit?: number;
  uploadLimit?: number;
}

export interface TorrentSettings {
  downloadPath: string;
  maxDownloadSpeed: number;
  maxUploadSpeed: number;
  maxConnections: number;
  startPaused: boolean;
}

export interface TorrentError {
  code: string;
  message: string;
  details?: string;
} 
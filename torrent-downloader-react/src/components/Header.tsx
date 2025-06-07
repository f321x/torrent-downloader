import { Download, Upload, Folder, Settings, Wifi } from 'lucide-react';
import { TorrentInfo } from '../services/torrentService';
import { formatSpeed } from '../utils/formatters';

interface HeaderProps {
  torrents: TorrentInfo[];
  onOpenDownloads: () => void;
  onShowSettings?: () => void;
}

export const Header = ({ torrents, onOpenDownloads, onShowSettings }: HeaderProps) => {
  const totalDownloadSpeed = torrents.reduce((sum, t) => sum + t.download_speed, 0);
  const totalUploadSpeed = torrents.reduce((sum, t) => sum + t.upload_speed, 0);
  const activeTorrents = torrents.filter(t => t.state === 'downloading').length;
  const seedingTorrents = torrents.filter(t => t.state === 'seeding').length;

  return (
    <header className="app-header">
      <div className="header-main">
        <div className="header-brand">
          <h1>Torrent Downloader</h1>
          <div className="connection-status">
            <Wifi size={16} className="status-icon online" />
            <span>Connected</span>
          </div>
        </div>

        <div className="header-stats">
          <div className="stat-group">
            <div className="stat-item-header">
              <Download size={16} className="stat-icon download" />
              <span className="stat-label">Down</span>
              <span className="stat-value">{formatSpeed(totalDownloadSpeed)}</span>
            </div>
            <div className="stat-item-header">
              <Upload size={16} className="stat-icon upload" />
              <span className="stat-label">Up</span>
              <span className="stat-value">{formatSpeed(totalUploadSpeed)}</span>
            </div>
          </div>
          
          <div className="stat-group">
            <div className="stat-item-header">
              <span className="stat-count">{activeTorrents}</span>
              <span className="stat-label">Downloading</span>
            </div>
            <div className="stat-item-header">
              <span className="stat-count">{seedingTorrents}</span>
              <span className="stat-label">Seeding</span>
            </div>
          </div>
        </div>

        <div className="header-actions">
          <button
            onClick={onOpenDownloads}
            className="action-button secondary"
            title="Open Downloads Folder"
          >
            <Folder size={18} />
            Downloads
          </button>
          
          {onShowSettings && (
            <button
              onClick={onShowSettings}
              className="action-button secondary"
              title="Settings"
            >
              <Settings size={18} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}; 
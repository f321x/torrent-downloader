import { useState } from 'react';
import { Download, Upload, Clock, HardDrive, Trash2, Play, Pause, MoreVertical } from 'lucide-react';
import { TorrentInfo } from '../services/torrentService';
import { formatBytes, formatSpeed, formatTime, formatProgress, getStateColor } from '../utils/formatters';
import clsx from 'clsx';

interface TorrentCardProps {
  torrent: TorrentInfo;
  onRemove: (id: string) => void;
  onPause?: (id: string) => void;
  onResume?: (id: string) => void;
}

export const TorrentCard = ({ torrent, onRemove, onPause, onResume }: TorrentCardProps) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  const handleRemove = async () => {
    setIsRemoving(true);
    try {
      await onRemove(torrent.id);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      setIsRemoving(false);
    }
  };

  const getStatusBadge = () => {
    const baseClass = "px-2 py-1 rounded-full text-xs font-medium uppercase tracking-wide";
    
    switch (torrent.state) {
      case 'downloading':
        return <span className={clsx(baseClass, "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200")}>Downloading</span>;
      case 'seeding':
        return <span className={clsx(baseClass, "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200")}>Seeding</span>;
      case 'finished':
        return <span className={clsx(baseClass, "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200")}>Finished</span>;
      case 'checking':
        return <span className={clsx(baseClass, "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200")}>Checking</span>;
      default:
        return <span className={clsx(baseClass, "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200")}>Unknown</span>;
    }
  };

  return (
    <div className="torrent-card">
      <div className="torrent-card-header">
        <div className="torrent-title-section">
          <h3 className="torrent-title">{torrent.name}</h3>
          {getStatusBadge()}
        </div>
        <div className="torrent-actions">
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="action-button secondary"
              aria-label="More actions"
            >
              <MoreVertical size={16} />
            </button>
            {showMenu && (
              <div className="action-menu">
                {torrent.state === 'downloading' ? (
                  <button
                    onClick={() => {
                      onPause?.(torrent.id);
                      setShowMenu(false);
                    }}
                    className="menu-item"
                  >
                    <Pause size={14} />
                    Pause
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      onResume?.(torrent.id);
                      setShowMenu(false);
                    }}
                    className="menu-item"
                  >
                    <Play size={14} />
                    Resume
                  </button>
                )}
                <button
                  onClick={() => {
                    handleRemove();
                    setShowMenu(false);
                  }}
                  className="menu-item danger"
                  disabled={isRemoving}
                >
                  <Trash2 size={14} />
                  {isRemoving ? 'Removing...' : 'Remove'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="torrent-progress-section">
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${torrent.progress}%`,
                backgroundColor: getStateColor(torrent.state)
              }}
            />
          </div>
          <span className="progress-text">{formatProgress(torrent.progress)}</span>
        </div>
      </div>

      <div className="torrent-stats">
        <div className="stat-item">
          <Download size={16} className="stat-icon" />
          <span className="stat-value">{formatSpeed(torrent.download_speed)}</span>
        </div>
        <div className="stat-item">
          <Upload size={16} className="stat-icon" />
          <span className="stat-value">{formatSpeed(torrent.upload_speed)}</span>
        </div>
        <div className="stat-item">
          <HardDrive size={16} className="stat-icon" />
          <span className="stat-value">{formatBytes(torrent.downloaded)} / {formatBytes(torrent.total_size)}</span>
        </div>
        <div className="stat-item">
          <Clock size={16} className="stat-icon" />
          <span className="stat-value">{formatTime(torrent.eta_seconds)}</span>
        </div>
      </div>
    </div>
  );
}; 
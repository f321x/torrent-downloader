import { useState, useRef } from 'react';
import { Link, Upload, Plus } from 'lucide-react';
import clsx from 'clsx';

interface AddTorrentProps {
  onAddMagnet: (magnetLink: string) => Promise<void>;
  onAddFile?: (file: File) => Promise<void>;
  isLoading: boolean;
}

export const AddTorrent = ({ onAddMagnet, onAddFile, isLoading }: AddTorrentProps) => {
  const [magnetLink, setMagnetLink] = useState('');
  const [activeTab, setActiveTab] = useState<'magnet' | 'file'>('magnet');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleMagnetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (magnetLink.trim()) {
      await onAddMagnet(magnetLink.trim());
      setMagnetLink('');
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onAddFile) {
      await onAddFile(file);
      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const isValidMagnet = (link: string): boolean => {
    return link.startsWith('magnet:') && link.includes('xt=urn:btih:');
  };

  return (
    <div className="add-torrent-container">
      <div className="tab-selector">
        <button
          onClick={() => setActiveTab('magnet')}
          className={clsx('tab-button', { active: activeTab === 'magnet' })}
        >
          <Link size={16} />
          Magnet Link
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={clsx('tab-button', { active: activeTab === 'file' })}
        >
          <Upload size={16} />
          Torrent File
        </button>
      </div>

      {activeTab === 'magnet' && (
        <form onSubmit={handleMagnetSubmit} className="add-torrent-form">
          <div className="input-group">
            <input
              type="text"
              value={magnetLink}
              onChange={(e) => setMagnetLink(e.target.value)}
              placeholder="Paste magnet link here..."
              disabled={isLoading}
              className={clsx('torrent-input', {
                'invalid': magnetLink && !isValidMagnet(magnetLink)
              })}
            />
            <button
              type="submit"
              disabled={isLoading || !magnetLink.trim() || !isValidMagnet(magnetLink)}
              className="add-button"
            >
              {isLoading ? (
                <div className="loading-spinner small" />
              ) : (
                <>
                  <Plus size={16} />
                  Add Torrent
                </>
              )}
            </button>
          </div>
          {magnetLink && !isValidMagnet(magnetLink) && (
            <p className="input-error">Please enter a valid magnet link</p>
          )}
        </form>
      )}

      {activeTab === 'file' && (
        <div className="file-upload-section">
          <input
            ref={fileInputRef}
            type="file"
            accept=".torrent"
            onChange={handleFileChange}
            disabled={isLoading || !onAddFile}
            className="file-input"
            id="torrent-file"
          />
          <label htmlFor="torrent-file" className="file-upload-label">
            <Upload size={24} />
            <span>Choose .torrent file or drag & drop</span>
          </label>
          {!onAddFile && (
            <p className="file-upload-notice">File upload will be available in a future update</p>
          )}
        </div>
      )}
    </div>
  );
}; 
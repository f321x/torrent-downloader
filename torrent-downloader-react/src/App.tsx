import { useState, useEffect } from 'react'
import { torrentService, TorrentInfo } from './services/torrentService'
import './App.css'

function App() {
  const [magnetLink, setMagnetLink] = useState('')
  const [torrents, setTorrents] = useState<TorrentInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [addingTorrent, setAddingTorrent] = useState<{
    status: 'idle' | 'loading' | 'success' | 'error';
    message: string;
  }>({
    status: 'idle',
    message: '',
  })

  // Fetch torrents periodically
  useEffect(() => {
    const fetchTorrents = async () => {
      try {
        const data = await torrentService.listTorrents()
        setTorrents(data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch torrents')
        console.error('Error fetching torrents:', err)
      }
    }

    // Initial fetch
    fetchTorrents()

    // Set up polling
    const interval = setInterval(fetchTorrents, 1000)

    // Cleanup
    return () => clearInterval(interval)
  }, [])

  const handleAddTorrent = async () => {
    if (!magnetLink.trim()) return
    
    setIsLoading(true)
    setError(null)
    setAddingTorrent({
      status: 'loading',
      message: 'Connecting to trackers...',
    })
    
    try {
      // First message after a short delay
      const messageTimer1 = setTimeout(() => {
        setAddingTorrent({
          status: 'loading',
          message: 'Fetching torrent metadata...',
        })
      }, 1000)

      // Second message after another delay
      const messageTimer2 = setTimeout(() => {
        setAddingTorrent({
          status: 'loading',
          message: 'Waiting for peers...',
        })
      }, 3000)

      const result = await torrentService.addTorrent(magnetLink)
      
      // Clear any pending timers to prevent message changes after success
      clearTimeout(messageTimer1)
      clearTimeout(messageTimer2)
      
      setMagnetLink('')
      setAddingTorrent({
        status: 'success',
        message: result.message || 'Torrent added successfully!',
      })
      
      // Reset status after showing success message
      setTimeout(() => {
        setAddingTorrent({
          status: 'idle',
          message: '',
        })
      }, 3000)
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to add torrent'
      setError(errorMessage)
      setAddingTorrent({
        status: 'error',
        message: errorMessage,
      })
      console.error('Error adding torrent:', err)
      
      // Reset status after showing error message
      setTimeout(() => {
        setAddingTorrent({
          status: 'idle',
          message: '',
        })
      }, 5000)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemoveTorrent = async (id: string) => {
    try {
      await torrentService.removeTorrent(id)
      setTorrents(torrents.filter(t => t.id !== id))
      setError(null)
    } catch (err) {
      setError('Failed to remove torrent')
      console.error('Error removing torrent:', err)
    }
  }

  const handleOpenDownloads = async () => {
    try {
      await torrentService.openDownloadsFolder()
      setError(null)
    } catch (err) {
      setError('Failed to open downloads folder')
      console.error('Error opening downloads folder:', err)
    }
  }

  const formatSpeed = (speed: number): string => {
    if (speed > 1024) {
      return `${(speed / 1024).toFixed(2)} MB/s`
    }
    return `${speed.toFixed(2)} KB/s`
  }

  const formatTime = (seconds: number | null): string => {
    if (seconds === null) {
      return 'Calculating...'
    }
    
    if (seconds === 0) {
      return 'Complete'
    }
    
    if (seconds < 0 || isNaN(seconds)) {
      return 'Unknown'
    }
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = Math.floor(seconds % 60)

    if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    } else {
      return `${remainingSeconds}s`
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Torrent Downloader</h1>
        <div className="header-buttons">
          <button onClick={handleOpenDownloads}>Open Downloads</button>
        </div>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="input-section">
        <input
          type="text"
          value={magnetLink}
          onChange={(e) => setMagnetLink(e.target.value)}
          placeholder="Enter magnet link..."
          disabled={isLoading}
        />
        <button onClick={handleAddTorrent} disabled={isLoading || !magnetLink.trim()}>
          Add Torrent
        </button>
      </div>
      
      {addingTorrent.status !== 'idle' && (
        <div className={`torrent-status-message ${addingTorrent.status}`}>
          <div className="status-content">
            {addingTorrent.status === 'loading' && (
              <div className="loading-spinner"></div>
            )}
            {addingTorrent.status === 'success' && (
              <div className="status-icon success-icon">✓</div>
            )}
            {addingTorrent.status === 'error' && (
              <div className="status-icon error-icon">✕</div>
            )}
            <p>{addingTorrent.message}</p>
          </div>
        </div>
      )}

      <div className="torrents-list">
        {torrents.map((torrent) => (
          <div key={torrent.id} className="torrent-item">
            <div className="torrent-info">
              <div className="torrent-header">
                <h3>{torrent.name}</h3>
                <div className="torrent-actions">
                  <button 
                    onClick={() => handleRemoveTorrent(torrent.id)}
                    className="remove-button"
                  >
                    Remove
                  </button>
                </div>
              </div>
              <p>Status: {torrent.state}</p>
              <p>↓ {formatSpeed(torrent.download_speed)} | ↑ {formatSpeed(torrent.upload_speed)}</p>
              <p>Progress: {torrent.progress.toFixed(1)}% | Time remaining: {formatTime(torrent.eta_seconds)}</p>
            </div>
            <div className="progress-bar">
              <div 
                className="progress" 
                style={{ width: `${torrent.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App

import { useState, useEffect } from 'react'
import { torrentService, TorrentInfo } from './services/torrentService'
import './App.css'

function App() {
  const [magnetLink, setMagnetLink] = useState('')
  const [torrents, setTorrents] = useState<TorrentInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
    
    try {
      await torrentService.addTorrent(magnetLink)
      setMagnetLink('')
    } catch (err) {
      setError('Failed to add torrent')
      console.error('Error adding torrent:', err)
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

  return (
    <div className="container">
      <header>
        <h1>Torrent Downloader</h1>
        <button onClick={handleOpenDownloads}>Open Downloads</button>
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

      <div className="torrents-list">
        {torrents.map((torrent) => (
          <div key={torrent.id} className="torrent-item">
            <div className="torrent-info">
              <div className="torrent-header">
                <h3>{torrent.name}</h3>
                <button 
                  onClick={() => handleRemoveTorrent(torrent.id)}
                  className="remove-button"
                >
                  Remove
                </button>
              </div>
              <p>Status: {torrent.state}</p>
              <p>Speed: {formatSpeed(torrent.download_speed)}</p>
              <p>Progress: {torrent.progress.toFixed(1)}%</p>
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

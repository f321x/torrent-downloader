import { useState, useEffect } from 'react'
import { torrentService, TorrentInfo } from './services/torrentService'
import './App.css'

function App() {
  const [magnetLink, setMagnetLink] = useState('')
  const [torrents, setTorrents] = useState<TorrentInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({})

  // Fetch torrents periodically
  useEffect(() => {
    const fetchTorrents = async () => {
      try {
        const data = await torrentService.listTorrents()
        console.log('Fetched torrents:', data)  // Log fetched data
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

  const handlePauseTorrent = async (id: string) => {
    try {
      setLoadingStates(prev => ({ ...prev, [id]: true }))
      await torrentService.pauseTorrent(id)
      console.log('Pausing torrent:', id)  // Log pause action
      // Immediately update the UI
      setTorrents(prev => {
        const updated = prev.map(t => 
          t.id === id ? { ...t, state: 'paused', download_speed: 0, upload_speed: 0 } : t
        )
        console.log('Updated torrents after pause:', updated)  // Log updated state
        return updated
      })
      setError(null)
    } catch (err) {
      setError('Failed to pause torrent')
      console.error('Error pausing torrent:', err)
    } finally {
      setLoadingStates(prev => ({ ...prev, [id]: false }))
    }
  }

  const handleResumeTorrent = async (id: string) => {
    try {
      setLoadingStates(prev => ({ ...prev, [id]: true }))
      await torrentService.resumeTorrent(id)
      console.log('Resuming torrent:', id)  // Log resume action
      // Immediately update the UI
      setTorrents(prev => {
        const updated = prev.map(t => 
          t.id === id ? { ...t, state: 'downloading' } : t
        )
        console.log('Updated torrents after resume:', updated)  // Log updated state
        return updated
      })
      setError(null)
    } catch (err) {
      setError('Failed to resume torrent')
      console.error('Error resuming torrent:', err)
    } finally {
      setLoadingStates(prev => ({ ...prev, [id]: false }))
    }
  }

  const handlePauseAll = async () => {
    try {
      await torrentService.pauseAllTorrents()
      setError(null)
    } catch (err) {
      setError('Failed to pause all torrents')
      console.error('Error pausing all torrents:', err)
    }
  }

  const handleResumeAll = async () => {
    try {
      await torrentService.resumeAllTorrents()
      setError(null)
    } catch (err) {
      setError('Failed to resume all torrents')
      console.error('Error resuming all torrents:', err)
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
        <div className="header-buttons">
          <button onClick={handleOpenDownloads}>Open Downloads</button>
          {torrents.length > 0 && (
            <>
              <button onClick={handlePauseAll}>Pause All</button>
              <button onClick={handleResumeAll}>Resume All</button>
            </>
          )}
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

      <div className="torrents-list">
        {torrents.map((torrent) => {
          console.log('Rendering torrent:', torrent.id, 'State:', torrent.state)  // Log render state
          return (
            <div key={torrent.id} className="torrent-item">
              <div className="torrent-info">
                <div className="torrent-header">
                  <h3>{torrent.name}</h3>
                  <div className="torrent-actions">
                    {torrent.state === 'paused' ? (
                      <button 
                        onClick={() => handleResumeTorrent(torrent.id)}
                        className="resume-button"
                        disabled={loadingStates[torrent.id] || loadingStates.all}
                      >
                        {loadingStates[torrent.id] ? 'Resuming...' : 'Resume'}
                      </button>
                    ) : (
                      <button 
                        onClick={() => handlePauseTorrent(torrent.id)}
                        className="pause-button"
                        disabled={loadingStates[torrent.id] || loadingStates.all}
                      >
                        {loadingStates[torrent.id] ? 'Pausing...' : 'Pause'}
                      </button>
                    )}
                    <button 
                      onClick={() => handleRemoveTorrent(torrent.id)}
                      className="remove-button"
                    >
                      Remove
                    </button>
                  </div>
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
          )
        })}
      </div>
    </div>
  )
}

export default App

import { useState, useEffect, useCallback } from 'react'
import { Toaster, toast } from 'react-hot-toast'
import { torrentService, TorrentInfo } from './services/torrentService'
import { Header } from './components/Header'
import { AddTorrent } from './components/AddTorrent'
import { TorrentCard } from './components/TorrentCard'
import { StatusMessage } from './components/StatusMessage'
import './App.css'

function App() {
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
  const [pollInterval, setPollInterval] = useState(1000)

  // Smart polling - adjust interval based on activity
  const updatePollInterval = useCallback((torrents: TorrentInfo[]) => {
    const activeTorrents = torrents.filter(t => 
      t.state === 'downloading' || t.state === 'checking'
    )
    
    if (activeTorrents.length === 0) {
      setPollInterval(5000) // Slow polling when idle
    } else {
      setPollInterval(1000) // Fast polling when active
    }
  }, [])

  // Fetch torrents with error handling and retry logic
  const fetchTorrents = useCallback(async () => {
    try {
      const data = await torrentService.listTorrents()
      setTorrents(data)
      updatePollInterval(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching torrents:', err)
      // Don't show error toast for fetch failures to avoid spam
      setError('Connection lost. Retrying...')
    }
  }, [updatePollInterval])

  // Initial fetch and polling setup
  useEffect(() => {
    fetchTorrents()
    const interval = setInterval(fetchTorrents, pollInterval)
    return () => clearInterval(interval)
  }, [fetchTorrents, pollInterval])

  const handleAddMagnet = async (magnetLink: string) => {
    setIsLoading(true)
    setError(null)
    setAddingTorrent({
      status: 'loading',
      message: 'Connecting to trackers...',
    })
    
    try {
      // Progressive loading messages
      const messageTimer1 = setTimeout(() => {
        setAddingTorrent({
          status: 'loading',
          message: 'Fetching torrent metadata...',
        })
      }, 1000)

      const messageTimer2 = setTimeout(() => {
        setAddingTorrent({
          status: 'loading',
          message: 'Waiting for peers...',
        })
      }, 3000)

      const result = await torrentService.addTorrent(magnetLink)
      
      clearTimeout(messageTimer1)
      clearTimeout(messageTimer2)
      
      setAddingTorrent({
        status: 'success',
        message: result.message || 'Torrent added successfully!',
      })

      toast.success(`Added: ${result.message || 'Torrent added successfully!'}`)
      
      // Immediate fetch to show new torrent
      fetchTorrents()
      
      setTimeout(() => {
        setAddingTorrent({ status: 'idle', message: '' })
      }, 3000)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add torrent'
      setError(errorMessage)
      setAddingTorrent({
        status: 'error',
        message: errorMessage,
      })
      
      toast.error(errorMessage)
      
      setTimeout(() => {
        setAddingTorrent({ status: 'idle', message: '' })
      }, 5000)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemoveTorrent = async (id: string) => {
    try {
      await torrentService.removeTorrent(id)
      setTorrents(torrents.filter(t => t.id !== id))
      toast.success('Torrent removed successfully')
      setError(null)
    } catch (err) {
      const errorMessage = 'Failed to remove torrent'
      setError(errorMessage)
      toast.error(errorMessage)
      console.error('Error removing torrent:', err)
    }
  }

  const handleOpenDownloads = async () => {
    try {
      await torrentService.openDownloadsFolder()
      toast.success('Downloads folder opened')
      setError(null)
    } catch (err) {
      const errorMessage = 'Failed to open downloads folder'
      setError(errorMessage)
      toast.error(errorMessage)
      console.error('Error opening downloads folder:', err)
    }
  }

  const handlePauseTorrent = async (id: string) => {
    try {
      await torrentService.pauseTorrent(id)
      toast.success('Torrent paused successfully')
      setError(null)
      // Immediate fetch to update torrent state
      fetchTorrents()
    } catch (err) {
      const errorMessage = 'Failed to pause torrent'
      setError(errorMessage)
      toast.error(errorMessage)
      console.error('Error pausing torrent:', err)
    }
  }

  const handleResumeTorrent = async (id: string) => {
    try {
      await torrentService.resumeTorrent(id)
      toast.success('Torrent resumed successfully')
      setError(null)
      // Immediate fetch to update torrent state
      fetchTorrents()
    } catch (err) {
      const errorMessage = 'Failed to resume torrent'
      setError(errorMessage)
      toast.error(errorMessage)
      console.error('Error resuming torrent:', err)
    }
  }

  return (
    <div className="app">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--background-primary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
          },
        }}
      />
      
      <Header 
        torrents={torrents}
        onOpenDownloads={handleOpenDownloads}
      />

      <main className="main-content">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
          </div>
        )}

        <AddTorrent
          onAddMagnet={handleAddMagnet}
          isLoading={isLoading}
        />
        
        <StatusMessage
          status={addingTorrent.status}
          message={addingTorrent.message}
        />

        <div className="torrents-section">
          {torrents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-content">
                <h3>No torrents yet</h3>
                <p>Add a magnet link above to get started downloading torrents</p>
              </div>
            </div>
          ) : (
            <div className="torrents-grid">
              {torrents.map((torrent) => (
                <TorrentCard
                  key={torrent.id}
                  torrent={torrent}
                  onRemove={handleRemoveTorrent}
                  onPause={handlePauseTorrent}
                  onResume={handleResumeTorrent}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App

import { useState, useEffect, useCallback } from 'react';
import { torrentService, TorrentInfo } from '../services/torrentService';

interface UseTorrentsReturn {
  torrents: TorrentInfo[];
  isLoading: boolean;
  error: string | null;
  addTorrent: (magnetLink: string) => Promise<{ success: boolean; message: string }>;
  removeTorrent: (id: string) => Promise<void>;
  refetchTorrents: () => Promise<void>;
}

export const useTorrents = (): UseTorrentsReturn => {
  const [torrents, setTorrents] = useState<TorrentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState(1000);

  // Smart polling - adjust interval based on activity
  const updatePollInterval = useCallback((torrents: TorrentInfo[]) => {
    const activeTorrents = torrents.filter(t => 
      t.state === 'downloading' || t.state === 'checking'
    );
    
    if (activeTorrents.length === 0) {
      setPollInterval(5000); // Slow polling when idle
    } else {
      setPollInterval(1000); // Fast polling when active
    }
  }, []);

  // Fetch torrents with error handling
  const fetchTorrents = useCallback(async () => {
    try {
      const data = await torrentService.listTorrents();
      setTorrents(data);
      updatePollInterval(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching torrents:', err);
      setError('Connection lost. Retrying...');
    }
  }, [updatePollInterval]);

  // Set up polling
  useEffect(() => {
    fetchTorrents();
    const interval = setInterval(fetchTorrents, pollInterval);
    return () => clearInterval(interval);
  }, [fetchTorrents, pollInterval]);

  const addTorrent = useCallback(async (magnetLink: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await torrentService.addTorrent(magnetLink);
      
      // Immediate fetch to show new torrent
      await fetchTorrents();
      
      return {
        success: true,
        message: result.message || 'Torrent added successfully!'
      };
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add torrent';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage
      };
    } finally {
      setIsLoading(false);
    }
  }, [fetchTorrents]);

  const removeTorrent = useCallback(async (id: string) => {
    try {
      await torrentService.removeTorrent(id);
      setTorrents(prev => prev.filter(t => t.id !== id));
      setError(null);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      const errorMessage = 'Failed to remove torrent';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  return {
    torrents,
    isLoading,
    error,
    addTorrent,
    removeTorrent,
    refetchTorrents: fetchTorrents
  };
}; 
import { useState, useEffect, useCallback } from 'react';
import WebTorrent from 'webtorrent';
import { TorrentData, TorrentState, AddTorrentOptions } from '../types/torrent';

export function useTorrentManager() {
  const [state, setState] = useState<TorrentState>({
    torrents: {},
    client: null,
  });

  // Initialize WebTorrent client
  useEffect(() => {
    const client = new WebTorrent();
    setState(prev => ({ ...prev, client }));

    return () => {
      client.destroy();
    };
  }, []);

  // Update torrent data periodically
  useEffect(() => {
    if (!state.client) return;

    const interval = setInterval(() => {
      const torrents: Record<string, TorrentData> = {};

      state.client.torrents.forEach(torrent => {
        torrents[torrent.infoHash] = {
          infoHash: torrent.infoHash,
          name: torrent.name,
          progress: torrent.progress,
          downloadSpeed: torrent.downloadSpeed,
          uploadSpeed: torrent.uploadSpeed,
          numPeers: torrent.numPeers,
          timeRemaining: torrent.timeRemaining,
          size: torrent.length,
          downloaded: torrent.downloaded,
          status: torrent.done ? 'complete' : 'downloading',
        };
      });

      setState(prev => ({
        ...prev,
        torrents,
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [state.client]);

  const addTorrent = useCallback(
    ({ magnetUri }: AddTorrentOptions) => {
      if (!state.client) return;

      try {
        state.client.add(magnetUri, {}, torrent => {
          const torrentData: TorrentData = {
            infoHash: torrent.infoHash,
            name: torrent.name,
            progress: 0,
            downloadSpeed: 0,
            uploadSpeed: 0,
            numPeers: 0,
            timeRemaining: 0,
            size: torrent.length,
            downloaded: 0,
            status: 'downloading',
          };

          setState(prev => ({
            ...prev,
            torrents: {
              ...prev.torrents,
              [torrent.infoHash]: torrentData,
            },
          }));

          // Handle torrent events
          torrent.on('error', error => {
            setState(prev => ({
              ...prev,
              torrents: {
                ...prev.torrents,
                [torrent.infoHash]: {
                  ...prev.torrents[torrent.infoHash],
                  status: 'error',
                  error: error.message,
                },
              },
            }));
          });

          torrent.on('done', () => {
            setState(prev => ({
              ...prev,
              torrents: {
                ...prev.torrents,
                [torrent.infoHash]: {
                  ...prev.torrents[torrent.infoHash],
                  status: 'complete',
                  progress: 1,
                },
              },
            }));
          });
        });
      } catch (error) {
        console.error('Error adding torrent:', error);
      }
    },
    [state.client]
  );

  const removeTorrent = useCallback(
    (infoHash: string) => {
      if (!state.client) return;

      const torrent = state.client.torrents.find(t => t.infoHash === infoHash);
      if (torrent) {
        torrent.destroy();
        setState(prev => {
          const torrents = { ...prev.torrents };
          delete torrents[infoHash];
          return { ...prev, torrents };
        });
      }
    },
    [state.client]
  );

  const pauseTorrent = useCallback(
    (infoHash: string) => {
      if (!state.client) return;

      const torrent = state.client.torrents.find(t => t.infoHash === infoHash);
      if (torrent) {
        torrent.pause();
        setState(prev => ({
          ...prev,
          torrents: {
            ...prev.torrents,
            [infoHash]: {
              ...prev.torrents[infoHash],
              status: 'paused',
            },
          },
        }));
      }
    },
    [state.client]
  );

  const resumeTorrent = useCallback(
    (infoHash: string) => {
      if (!state.client) return;

      const torrent = state.client.torrents.find(t => t.infoHash === infoHash);
      if (torrent) {
        torrent.resume();
        setState(prev => ({
          ...prev,
          torrents: {
            ...prev.torrents,
            [infoHash]: {
              ...prev.torrents[infoHash],
              status: 'downloading',
            },
          },
        }));
      }
    },
    [state.client]
  );

  return {
    torrents: state.torrents,
    addTorrent,
    removeTorrent,
    pauseTorrent,
    resumeTorrent,
  };
} 
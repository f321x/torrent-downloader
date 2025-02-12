import { useState } from 'react';
import { TextInput, Button, Group, Paper } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { useTorrentStore } from '../store/torrentStore';

export function AddTorrent() {
  const [magnetUri, setMagnetUri] = useState('');
  const addTorrent = useTorrentStore(state => state.addTorrent);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!magnetUri.trim()) return;

    try {
      await addTorrent({ magnetUri });
      setMagnetUri('');
    } catch (error) {
      console.error('Failed to add torrent:', error);
    }
  };

  return (
    <Paper p="md" radius="md">
      <form onSubmit={handleSubmit}>
        <Group>
          <TextInput
            placeholder="Enter magnet link"
            value={magnetUri}
            onChange={(e) => setMagnetUri(e.target.value)}
            style={{ flex: 1 }}
            data-autofocus
          />
          <Button
            leftIcon={<IconPlus size={16} />}
            type="submit"
            disabled={!magnetUri.trim()}
          >
            Add Torrent
          </Button>
        </Group>
      </form>
    </Paper>
  );
} 
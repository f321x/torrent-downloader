import { Table, Progress, ActionIcon, Group, Text } from '@mantine/core';
import { IconPlayerPause, IconPlayerPlay, IconTrash } from '@tabler/icons-react';
import { useTorrentStore } from '../store/torrentStore';
import { TorrentState } from '../types/torrent';
import { formatSize, formatSpeed, formatTime, formatProgress, formatPeers } from '../utils/format';

export function TorrentList() {
  const torrents = useTorrentStore(state => state.torrents);
  const { pauseTorrent, resumeTorrent, removeTorrent } = useTorrentStore();

  const rows = Array.from(torrents.entries()).map(([id, torrent]) => (
    <tr key={id}>
      <td>
        <Text size="sm" weight={500}>
          {torrent.name}
        </Text>
      </td>
      <td>
        <Group position="apart" spacing="xs">
          <Text size="xs" color="dimmed">
            {formatProgress(torrent.progress)}
          </Text>
          <Progress
            value={torrent.progress * 100}
            size="sm"
            style={{ width: '100%', maxWidth: 100 }}
          />
        </Group>
      </td>
      <td>
        <Text size="sm">
          ↓ {formatSpeed(torrent.downloadSpeed)}
          <br />
          ↑ {formatSpeed(torrent.uploadSpeed)}
        </Text>
      </td>
      <td>
        <Text size="sm">
          {formatTime(torrent.remainingTime)}
        </Text>
      </td>
      <td>
        <Text size="sm">
          {formatPeers(torrent.peers)}
        </Text>
      </td>
      <td>
        <Group spacing={0} position="right">
          {torrent.state === TorrentState.Downloading ? (
            <ActionIcon onClick={() => pauseTorrent(id)}>
              <IconPlayerPause size={16} />
            </ActionIcon>
          ) : (
            <ActionIcon onClick={() => resumeTorrent(id)}>
              <IconPlayerPlay size={16} />
            </ActionIcon>
          )}
          <ActionIcon color="red" onClick={() => removeTorrent(id)}>
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </td>
    </tr>
  ));

  return (
    <Table verticalSpacing="sm">
      <thead>
        <tr>
          <th>Name</th>
          <th>Progress</th>
          <th>Speed</th>
          <th>ETA</th>
          <th>Peers</th>
          <th style={{ width: 100 }} />
        </tr>
      </thead>
      <tbody>
        {rows.length > 0 ? (
          rows
        ) : (
          <tr>
            <td colSpan={6}>
              <Text color="dimmed" align="center">
                No active torrents
              </Text>
            </td>
          </tr>
        )}
      </tbody>
    </Table>
  );
} 
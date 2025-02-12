import { useState } from 'react';
import {
  MantineProvider,
  AppShell,
  Text,
  Container,
  TextInput,
  Button,
  Group,
  Table,
  Progress,
  ActionIcon,
  Stack,
  Title,
  createTheme,
} from '@mantine/core';
import {
  IconDownload,
  IconPause,
  IconPlayerPlay,
  IconTrash,
} from '@tabler/icons-react';
import { useTorrentManager } from './hooks/useTorrentManager';
import { formatSize, formatSpeed, formatTime, formatProgress } from './utils/format';

const theme = createTheme({
  primaryColor: 'blue',
});

export default function App() {
  const [magnetUri, setMagnetUri] = useState('');
  const { torrents, addTorrent, removeTorrent, pauseTorrent, resumeTorrent } = useTorrentManager();

  const handleAddTorrent = () => {
    if (!magnetUri.trim()) return;
    addTorrent({ magnetUri: magnetUri.trim() });
    setMagnetUri('');
  };

  const torrentRows = Object.values(torrents).map((torrent) => (
    <Table.Tr key={torrent.infoHash}>
      <Table.Td style={{ maxWidth: '300px' }}>
        <Text truncate>{torrent.name}</Text>
      </Table.Td>
      <Table.Td>
        <Stack gap="xs">
          <Progress value={torrent.progress * 100} size="sm" />
          <Text size="sm" c="dimmed">
            {formatProgress(torrent.progress)}
          </Text>
        </Stack>
      </Table.Td>
      <Table.Td>
        <Stack gap={0}>
          <Text size="sm">↓ {formatSpeed(torrent.downloadSpeed)}</Text>
          <Text size="sm">↑ {formatSpeed(torrent.uploadSpeed)}</Text>
        </Stack>
      </Table.Td>
      <Table.Td>
        <Text>{formatTime(torrent.timeRemaining)}</Text>
      </Table.Td>
      <Table.Td>
        <Text>{torrent.numPeers}</Text>
      </Table.Td>
      <Table.Td>
        <Group gap="xs">
          {torrent.status === 'downloading' ? (
            <ActionIcon
              variant="light"
              color="blue"
              onClick={() => pauseTorrent(torrent.infoHash)}
            >
              <IconPause size={16} />
            </ActionIcon>
          ) : torrent.status === 'paused' ? (
            <ActionIcon
              variant="light"
              color="green"
              onClick={() => resumeTorrent(torrent.infoHash)}
            >
              <IconPlayerPlay size={16} />
            </ActionIcon>
          ) : null}
          <ActionIcon
            variant="light"
            color="red"
            onClick={() => removeTorrent(torrent.infoHash)}
          >
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <MantineProvider theme={theme} defaultColorScheme="auto">
      <AppShell
        header={{ height: 60 }}
        padding="md"
      >
        <AppShell.Header>
          <Container h="100%" py="md">
            <Group justify="space-between" h="100%">
              <Group gap="xs">
                <IconDownload size={24} />
                <Title order={1} size="h3">Torrent Downloader</Title>
              </Group>
            </Group>
          </Container>
        </AppShell.Header>

        <AppShell.Main>
          <Container size="xl">
            <Stack gap="lg">
              <Group>
                <TextInput
                  placeholder="Paste magnet link here..."
                  value={magnetUri}
                  onChange={(e) => setMagnetUri(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleAddTorrent();
                    }
                  }}
                  style={{ flex: 1 }}
                />
                <Button onClick={handleAddTorrent}>Add Magnet</Button>
              </Group>

              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Name</Table.Th>
                    <Table.Th>Progress</Table.Th>
                    <Table.Th>Speed</Table.Th>
                    <Table.Th>ETA</Table.Th>
                    <Table.Th>Peers</Table.Th>
                    <Table.Th>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {torrentRows}
                </Table.Tbody>
              </Table>
            </Stack>
          </Container>
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}

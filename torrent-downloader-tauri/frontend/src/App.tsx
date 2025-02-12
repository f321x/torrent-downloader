import { useEffect } from 'react';
import { MantineProvider, Box, Title, Container, Stack } from '@mantine/core';
import { AddTorrent } from './components/AddTorrent';
import { TorrentList } from './components/TorrentList';
import { useTorrentStore } from './store/torrentStore';

function App() {
  const initialize = useTorrentStore(state => state.initialize);

  useEffect(() => {
    initialize().catch(console.error);
  }, [initialize]);

  return (
    <MantineProvider
      theme={{
        primaryColor: 'blue',
        components: {
          Container: {
            defaultProps: {
              size: 'lg',
            },
          },
        },
      }}
    >
      <Box>
        <Box py="xs" mb="md" style={{ borderBottom: '1px solid #eee' }}>
          <Container size="lg">
            <Title order={1} size="h3">Torrent Downloader</Title>
          </Container>
        </Box>

        <Container>
          <Stack gap="md">
            <AddTorrent />
            <TorrentList />
          </Stack>
        </Container>
      </Box>
    </MantineProvider>
  );
}

export default App;

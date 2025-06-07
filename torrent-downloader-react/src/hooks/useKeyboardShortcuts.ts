import { useEffect } from 'react';

interface KeyboardShortcuts {
  openDownloads?: () => void;
  addTorrent?: () => void;
  closeModal?: () => void;
}

export const useKeyboardShortcuts = (shortcuts: KeyboardShortcuts) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore shortcuts when typing in inputs
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
        // Only handle Escape in inputs
        if (event.key === 'Escape' && shortcuts.closeModal) {
          shortcuts.closeModal();
        }
        return;
      }

      // Ctrl/Cmd + O: Open downloads folder
      if ((event.ctrlKey || event.metaKey) && event.key === 'o' && shortcuts.openDownloads) {
        event.preventDefault();
        shortcuts.openDownloads();
      }

      // Ctrl/Cmd + N: Focus add torrent input
      if ((event.ctrlKey || event.metaKey) && event.key === 'n' && shortcuts.addTorrent) {
        event.preventDefault();
        shortcuts.addTorrent();
      }

      // Escape: Close modals/menus
      if (event.key === 'Escape' && shortcuts.closeModal) {
        shortcuts.closeModal();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
}; 
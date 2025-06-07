export const formatBytes = (bytes: number, decimals = 2): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export const formatSpeed = (speed: number): string => {
  if (speed > 1024) {
    return `${(speed / 1024).toFixed(2)} MB/s`;
  }
  return `${speed.toFixed(2)} KB/s`;
};

export const formatTime = (seconds: number | null): string => {
  if (seconds === null) {
    return 'Calculating...';
  }
  
  if (seconds === 0) {
    return 'Complete';
  }
  
  if (seconds < 0 || isNaN(seconds)) {
    return 'Unknown';
  }
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

export const formatProgress = (progress: number): string => {
  return `${progress.toFixed(1)}%`;
};

export const getStateColor = (state: string): string => {
  switch (state) {
    case 'downloading':
      return '#2563eb';
    case 'seeding':
      return '#16a34a';
    case 'finished':
      return '#059669';
    case 'checking':
      return '#ea580c';
    default:
      return '#64748b';
  }
};

export const getStateIcon = (state: string): string => {
  switch (state) {
    case 'downloading':
      return '⬇️';
    case 'seeding':
      return '⬆️';
    case 'finished':
      return '✅';
    case 'checking':
      return '🔍';
    default:
      return '⏸️';
  }
}; 
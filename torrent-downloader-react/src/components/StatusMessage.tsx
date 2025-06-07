import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import clsx from 'clsx';

interface StatusMessageProps {
  status: 'idle' | 'loading' | 'success' | 'error';
  message: string;
  className?: string;
}

export const StatusMessage = ({ status, message, className }: StatusMessageProps) => {
  if (status === 'idle') return null;

  const getIcon = () => {
    switch (status) {
      case 'loading':
        return <Loader2 size={20} className="animate-spin" />;
      case 'success':
        return <CheckCircle size={20} className="text-green-500" />;
      case 'error':
        return <XCircle size={20} className="text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusClass = () => {
    switch (status) {
      case 'loading':
        return 'status-loading';
      case 'success':
        return 'status-success';
      case 'error':
        return 'status-error';
      default:
        return '';
    }
  };

  return (
    <div className={clsx('status-message', getStatusClass(), className)}>
      <div className="status-content">
        {getIcon()}
        <p className="status-text">{message}</p>
      </div>
    </div>
  );
}; 
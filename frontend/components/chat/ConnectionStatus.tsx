'use client';

interface ConnectionStatusProps {
  status: 'connecting' | 'connected' | 'disconnected';
}

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  const config = {
    connecting: {
      dot: 'bg-yellow-400 animate-pulse',
      text: 'text-yellow-600',
      label: '连接中'
    },
    connected: {
      dot: 'bg-green-500',
      text: 'text-green-600',
      label: '已连接'
    },
    disconnected: {
      dot: 'bg-red-500',
      text: 'text-red-600',
      label: '未连接'
    }
  };

  const { dot, text, label } = config[status];

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${dot}`} />
      <span className={`text-xs ${text}`}>{label}</span>
    </div>
  );
}

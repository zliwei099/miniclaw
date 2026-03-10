'use client';

import { useState } from 'react';
import { ToolCall } from './ChatContainer';
import { ChevronDown, ChevronUp, Loader2, CheckCircle, XCircle, Circle } from 'lucide-react';

interface ToolCallCardProps {
  toolCall: ToolCall;
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusConfig = {
    pending: {
      icon: <Circle className="w-4 h-4 text-gray-400" />,
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      label: '等待中'
    },
    running: {
      icon: <Loader2 className="w-4 h-4 animate-spin text-blue-500" />,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      label: '执行中'
    },
    completed: {
      icon: <CheckCircle className="w-4 h-4 text-green-500" />,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      label: '已完成'
    },
    error: {
      icon: <XCircle className="w-4 h-4 text-red-500" />,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      label: '出错'
    }
  };

  const config = statusConfig[toolCall.status];

  return (
    <div className={`rounded-lg border ${config.borderColor} ${config.bgColor} overflow-hidden text-sm`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-black/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          {config.icon}
          <span className="font-medium">{toolCall.name}</span>
          <span className="text-xs text-gray-500">({config.label})</span>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>
      
      {isExpanded && (
        <div className="px-3 pb-3 space-y-3 border-t border-gray-200/50">
          {/* 参数 */}
          <div className="pt-2">
            <div className="text-xs font-medium text-gray-500 mb-1">参数</div>
            <pre className="p-2 bg-white/50 rounded text-xs overflow-x-auto font-mono">
              {JSON.stringify(toolCall.parameters, null, 2)}
            </pre>
          </div>
          
          {/* 结果 */}
          {(toolCall.result !== undefined || toolCall.error) && (
            <div>
              <div className="text-xs font-medium text-gray-500 mb-1">
                {toolCall.error ? '错误' : '结果'}
              </div>
              <pre className={`p-2 rounded text-xs overflow-x-auto font-mono ${
                toolCall.error ? 'bg-red-100 text-red-800' : 'bg-white/50'
              }`}>
                {toolCall.error || JSON.stringify(toolCall.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

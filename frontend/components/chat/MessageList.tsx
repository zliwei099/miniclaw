'use client';

import { Message, ToolCall } from './ChatContainer';
import { ToolCallCard } from './ToolCallCard';
import { User, Bot } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  );
}

function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
        isUser ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-600'
      }`}>
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      
      {/* 消息内容 */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* 工具调用 */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mb-2">
            {message.toolCalls.map((toolCall) => (
              <ToolCallCard key={toolCall.id} toolCall={toolCall} />
            ))}
          </div>
        )}
        
        {/* 文本内容 */}
        <div className={`rounded-2xl px-5 py-3 ${
          isUser 
            ? 'bg-primary-500 text-white' 
            : 'bg-white border border-gray-200 text-gray-800'
        }`}>
          <div className="whitespace-pre-wrap leading-relaxed">
            {message.content || (message.isStreaming ? <span className="animate-pulse">▋</span> : '')}
          </div>
        </div>
        
        {/* 时间戳 */}
        <div className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : ''}`}>
          {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}

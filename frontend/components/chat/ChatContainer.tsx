'use client';

import { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { ConnectionStatus } from './ConnectionStatus';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: ToolCall[];
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ToolCall {
  id: string;
  name: string;
  parameters: Record<string, any>;
  result?: any;
  error?: string;
  status: 'pending' | 'running' | 'completed' | 'error';
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();
  
  const { sendMessage, lastMessage, connectionStatus } = useWebSocket('ws://localhost:8000/ws');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingContentRef = useRef('');

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 处理 WebSocket 消息
  useEffect(() => {
    if (!lastMessage) return;

    const data = lastMessage;
    
    switch (data.type) {
      case 'assistant_start':
        streamingContentRef.current = '';
        setMessages(prev => [...prev, {
          id: data.data.id,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
          toolCalls: [],
          isStreaming: true
        }]);
        setCurrentConversationId(data.data.conversation_id);
        break;
        
      case 'stream_chunk':
        streamingContentRef.current += data.data.content;
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.role === 'assistant' && lastMsg.isStreaming) {
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, content: streamingContentRef.current }
            ];
          }
          return prev;
        });
        break;
        
      case 'tool_call':
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMsg,
                toolCalls: [...(lastMsg.toolCalls || []), {
                  id: data.data.id,
                  name: data.data.name,
                  parameters: data.data.parameters,
                  status: data.data.status
                }]
              }
            ];
          }
          return prev;
        });
        break;
        
      case 'tool_result':
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.toolCalls) {
            const updatedCalls = lastMsg.toolCalls.map(call =>
              call.id === data.data.tool_call_id
                ? {
                    ...call,
                    status: data.data.status,
                    result: data.data.result,
                    error: data.data.error
                  }
                : call
            );
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, toolCalls: updatedCalls }
            ];
          }
          return prev;
        });
        break;
        
      case 'assistant_end':
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, isStreaming: false }
            ];
          }
          return prev;
        });
        setIsProcessing(false);
        break;
        
      case 'error':
        console.error('WebSocket error:', data.data.message);
        setIsProcessing(false);
        break;
    }
  }, [lastMessage]);

  const handleSend = async (content: string) => {
    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);
    
    // 发送 WebSocket 消息
    sendMessage({
      type: 'user_message',
      content,
      conversation_id: currentConversationId
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* 顶部状态栏 */}
      <header className="flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="text-2xl">🦞</div>
          <div>
            <h1 className="font-semibold text-gray-900">小小龙虾</h1>
            <p className="text-xs text-gray-500">MiniClaw AI Agent</p>
          </div>
        </div>
        
        <ConnectionStatus status={connectionStatus} />
      </header>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <div className="text-6xl mb-4">🦞</div>
            <p className="text-lg">你好！我是小小龙虾</p>
            <p className="text-sm">有什么可以帮你的吗？</p>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <InputBox 
        onSend={handleSend}
        disabled={isProcessing || connectionStatus !== 'connected'}
        placeholder={connectionStatus === 'connected' ? '输入消息...' : '等待连接...'}
      />
    </div>
  );
}

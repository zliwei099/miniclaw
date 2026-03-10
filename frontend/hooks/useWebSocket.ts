'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketReturn {
  sendMessage: (message: any) => void;
  lastMessage: any | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
}

// WebSocket 配置
const WS_CONFIG = {
  // 连接超时：5秒
  CONNECT_TIMEOUT: 5000,
  // 心跳间隔：30秒
  HEARTBEAT_INTERVAL: 30000,
  // 心跳超时：10秒
  HEARTBEAT_TIMEOUT: 10000,
  // 重连间隔：3秒
  RECONNECT_INTERVAL: 3000,
  // 最大重连次数
  MAX_RECONNECT_ATTEMPTS: 10
};

export function useWebSocket(url: string): UseWebSocketReturn {
  const [lastMessage, setLastMessage] = useState<any | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout>();
  const connectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const isManualCloseRef = useRef(false);

  // 清理所有定时器
  const clearAllTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    if (heartbeatTimeoutRef.current) clearTimeout(heartbeatTimeoutRef.current);
    if (connectTimeoutRef.current) clearTimeout(connectTimeoutRef.current);
  }, []);

  // 启动心跳
  const startHeartbeat = useCallback(() => {
    // 清除旧的心跳
    if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    if (heartbeatTimeoutRef.current) clearTimeout(heartbeatTimeoutRef.current);
    
    // 定时发送 ping
    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
        
        // 设置心跳超时检测
        heartbeatTimeoutRef.current = setTimeout(() => {
          console.warn('[WebSocket] 心跳超时，关闭连接');
          wsRef.current?.close();
        }, WS_CONFIG.HEARTBEAT_TIMEOUT);
      }
    }, WS_CONFIG.HEARTBEAT_INTERVAL);
  }, []);

  // 停止心跳
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    if (heartbeatTimeoutRef.current) clearTimeout(heartbeatTimeoutRef.current);
  }, []);

  // 连接 WebSocket
  const connect = useCallback(() => {
    // 检查重连次数
    if (reconnectAttemptsRef.current >= WS_CONFIG.MAX_RECONNECT_ATTEMPTS) {
      console.error('[WebSocket] 重连次数已达上限');
      setConnectionStatus('disconnected');
      return;
    }

    try {
      setConnectionStatus('connecting');
      reconnectAttemptsRef.current++;
      
      const ws = new WebSocket(url);
      wsRef.current = ws;
      isManualCloseRef.current = false;

      // 连接超时检测
      connectTimeoutRef.current = setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          console.warn('[WebSocket] 连接超时');
          ws.close();
        }
      }, WS_CONFIG.CONNECT_TIMEOUT);

      ws.onopen = () => {
        console.log('[WebSocket] 已连接');
        clearTimeout(connectTimeoutRef.current);
        reconnectAttemptsRef.current = 0;
        setConnectionStatus('connected');
        startHeartbeat();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 处理 pong 响应
          if (data.type === 'pong') {
            clearTimeout(heartbeatTimeoutRef.current);
            return;
          }
          
          setLastMessage(data);
        } catch (error) {
          console.error('[WebSocket] 消息解析失败:', error);
        }
      };

      ws.onclose = () => {
        console.log('[WebSocket] 连接关闭');
        stopHeartbeat();
        setConnectionStatus('disconnected');
        wsRef.current = null;
        
        // 非手动关闭时自动重连
        if (!isManualCloseRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`[WebSocket] 尝试重连... (${reconnectAttemptsRef.current}/${WS_CONFIG.MAX_RECONNECT_ATTEMPTS})`);
            connect();
          }, WS_CONFIG.RECONNECT_INTERVAL);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] 错误:', error);
        setConnectionStatus('disconnected');
      };
    } catch (error) {
      console.error('[WebSocket] 连接失败:', error);
      setConnectionStatus('disconnected');
    }
  }, [url, startHeartbeat, stopHeartbeat]);

  // 发送消息
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    } else {
      console.warn('[WebSocket] 未连接，无法发送消息');
      return false;
    }
  }, []);

  // 初始化连接
  useEffect(() => {
    connect();

    return () => {
      isManualCloseRef.current = true;
      clearAllTimers();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect, clearAllTimers]);

  return {
    sendMessage,
    lastMessage,
    connectionStatus
  };
}

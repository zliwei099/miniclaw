'use client';

import { useState } from 'react';
import { MessageSquare, Plus, Settings, Wrench } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  messageCount: number;
  createdAt: string;
}

export function Sidebar() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  const handleNewChat = () => {
    // 新建会话逻辑
    window.location.reload();
  };

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* 顶部 */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus size={18} />
          <span>新建会话</span>
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto p-2">
        <div className="text-xs font-medium text-gray-500 uppercase px-2 py-2">
          最近会话
        </div>
        
        {conversations.length === 0 ? (
          <div className="text-sm text-gray-400 px-2 py-4 text-center">
            暂无会话
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setActiveId(conv.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeId === conv.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <MessageSquare size={16} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">
                    {conv.title}
                  </div>
                  <div className="text-xs text-gray-400">
                    {conv.messageCount} 条消息
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 底部菜单 */}
      <div className="p-2 border-t border-gray-200 space-y-1">
        <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
          <Wrench size={16} />
          <span className="text-sm">工具管理</span>
        </button>
        
        <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
          <Settings size={16} />
          <span className="text-sm">设置</span>
        </button>
      </div>
    </aside>
  );
}

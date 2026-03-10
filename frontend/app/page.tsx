'use client';

import { ChatContainer } from '@/components/chat/ChatContainer';
import { Sidebar } from '@/components/sidebar/Sidebar';

export default function Home() {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <Sidebar />
      
      {/* 主聊天区域 */}
      <main className="flex-1 flex flex-col">
        <ChatContainer />
      </main>
    </div>
  );
}

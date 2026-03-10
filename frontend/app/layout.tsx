import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MiniClaw - 小小龙虾',
  description: '渐进式 AI Agent',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

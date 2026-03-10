# 小小龙虾 (MiniClaw) 可视化技术方案

## 方案对比

| 方案 | 开发成本 | 美观度 | 扩展性 | 适用场景 |
|------|----------|--------|--------|----------|
| **Gradio** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 快速原型、个人使用 |
| **Streamlit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 数据应用、内部工具 |
| **Next.js + React** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 产品级、多用户 |
| **Chainlit** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | AI Agent 专用 |

---

## 推荐方案 A: Next.js + React (产品级)

### 技术栈
```
前端:
├── Next.js 14 (App Router)
├── React 18 + TypeScript
├── Tailwind CSS + shadcn/ui
├── Zustand (状态管理)
├── React Query (数据获取)
└── Socket.io-client (实时通信)

后端:
├── FastAPI (Python) / Next.js API Routes
├── WebSocket / Server-Sent Events
├── SQLite / PostgreSQL
└── Redis (可选，消息队列)
```

### 核心界面结构
```
app/
├── page.tsx                    # 主界面
├── layout.tsx                  # 根布局
├── globals.css                 # 全局样式
│
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx   # 聊天主容器
│   │   ├── MessageList.tsx     # 消息列表
│   │   ├── MessageItem.tsx     # 单条消息
│   │   ├── InputBox.tsx        # 输入框
│   │   └── ToolCallCard.tsx    # 工具调用展示
│   │
│   ├── sidebar/
│   │   ├── Sidebar.tsx         # 侧边栏
│   │   ├── ConversationList.tsx # 会话列表
│   │   └── ToolManager.tsx     # 工具管理
│   │
│   ├── workflow/
│   │   ├── FlowEditor.tsx      # 工作流编辑器
│   │   ├── NodePalette.tsx     # 节点面板
│   │   └── PropertiesPanel.tsx # 属性面板
│   │
│   └── settings/
│       ├── ModelConfig.tsx     # 模型配置
│       └── MemoryViewer.tsx    # 记忆查看器
│
├── hooks/
│   ├── useWebSocket.ts         # WebSocket  hook
│   ├── useAgent.ts             # Agent 核心 hook
│   └── useTools.ts             # 工具管理 hook
│
└── lib/
    ├── api.ts                  # API 封装
    └── types.ts                # TypeScript 类型
```

### 核心组件设计

#### 1. 聊天界面
```tsx
// components/chat/ChatContainer.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { ToolCallCard } from './ToolCallCard';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: ToolCall[];
  timestamp: Date;
}

interface ToolCall {
  id: string;
  name: string;
  parameters: Record<string, any>;
  result?: any;
  status: 'pending' | 'running' | 'completed' | 'error';
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const { sendMessage, lastMessage, connectionStatus } = useWebSocket('ws://localhost:8000/ws');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 处理 WebSocket 消息
  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      
      switch (data.type) {
        case 'assistant_message':
          setMessages(prev => [...prev, {
            id: data.id,
            role: 'assistant',
            content: data.content,
            timestamp: new Date()
          }]);
          break;
          
        case 'tool_call':
          // 更新工具调用状态
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg.role === 'assistant') {
              const updatedMsg = {
                ...lastMsg,
                toolCalls: [...(lastMsg.toolCalls || []), data.toolCall]
              };
              return [...prev.slice(0, -1), updatedMsg];
            }
            return prev;
          });
          break;
          
        case 'tool_result':
          // 更新工具执行结果
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg.toolCalls) {
              const updatedCalls = lastMsg.toolCalls.map(call =>
                call.id === data.toolCallId 
                  ? { ...call, result: data.result, status: 'completed' }
                  : call
              );
              return [...prev.slice(0, -1), { ...lastMsg, toolCalls: updatedCalls }];
            }
            return prev;
          });
          break;
      }
    }
  }, [lastMessage]);

  const handleSend = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);
    
    sendMessage(JSON.stringify({
      type: 'user_message',
      content
    }));
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 顶部状态栏 */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-sm text-gray-600">
            {connectionStatus === 'connected' ? '已连接' : '未连接'}
          </span>
        </div>
        <h1 className="text-lg font-semibold">🦞 小小龙虾</h1>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">模型: GPT-4</span>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <InputBox 
        onSend={handleSend} 
        disabled={isProcessing || connectionStatus !== 'connected'}
      />
    </div>
  );
}
```

#### 2. 工具调用可视化
```tsx
// components/chat/ToolCallCard.tsx
'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Loader2, CheckCircle, XCircle } from 'lucide-react';

interface ToolCallCardProps {
  toolCall: {
    id: string;
    name: string;
    parameters: Record<string, any>;
    result?: any;
    status: 'pending' | 'running' | 'completed' | 'error';
  };
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusIcons = {
    pending: <div className="w-4 h-4 rounded-full bg-gray-300" />,
    running: <Loader2 className="w-4 h-4 animate-spin text-blue-500" />,
    completed: <CheckCircle className="w-4 h-4 text-green-500" />,
    error: <XCircle className="w-4 h-4 text-red-500" />
  };

  return (
    <div className="my-2 rounded-lg border bg-white shadow-sm overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          {statusIcons[toolCall.status]}
          <span className="font-medium text-sm">{toolCall.name}</span>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      
      {isExpanded && (
        <div className="px-3 pb-3 space-y-2">
          <div className="text-xs">
            <span className="text-gray-500 font-medium">参数:</span>
            <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
              {JSON.stringify(toolCall.parameters, null, 2)}
            </pre>
          </div>
          
          {toolCall.result && (
            <div className="text-xs">
              <span className="text-gray-500 font-medium">结果:</span>
              <pre className="mt-1 p-2 bg-green-50 rounded text-xs overflow-x-auto">
                {JSON.stringify(toolCall.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

#### 3. 工作流可视化编辑器
```tsx
// components/workflow/FlowEditor.tsx
'use client';

import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Node,
  Edge
} from 'reactflow';
import 'reactflow/dist/style.css';

const nodeTypes = {
  trigger: TriggerNode,
  llm: LLMNode,
  tool: ToolNode,
  condition: ConditionNode,
  output: OutputNode
};

export function FlowEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = (connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  };

  const addNode = (type: string) => {
    const newNode: Node = {
      id: `${type}-${Date.now()}`,
      type,
      position: { x: 100, y: 100 },
      data: { label: type }
    };
    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <div className="h-full flex">
      {/* 节点面板 */}
      <div className="w-64 bg-white border-r p-4">
        <h3 className="font-semibold mb-4">节点</h3>
        <div className="space-y-2">
          {Object.keys(nodeTypes).map((type) => (
            <button
              key={type}
              onClick={() => addNode(type)}
              className="w-full text-left px-3 py-2 rounded hover:bg-gray-100 border"
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* 画布 */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <Background />
        </ReactFlow>
      </div>

      {/* 属性面板 */}
      <div className="w-64 bg-white border-l p-4">
        <h3 className="font-semibold mb-4">属性</h3>
        {/* 选中节点的属性编辑器 */}
      </div>
    </div>
  );
}
```

---

## 推荐方案 B: Gradio (快速原型)

适合想最快看到效果的情况。

```python
# ui_gradio.py
import gradio as gr
from miniclaw.core import MiniClawCore

class GradioUI:
    def __init__(self):
        self.agent = MiniClawCore()
    
    def create_interface(self):
        with gr.Blocks(title="🦞 小小龙虾", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🦞 小小龙虾 - 你的 AI 助手")
            
            with gr.Row():
                # 左侧：聊天
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        height=500,
                        bubble_full_width=False
                    )
                    msg = gr.Textbox(
                        placeholder="输入消息...",
                        show_label=False
                    )
                    with gr.Row():
                        submit = gr.Button("发送", variant="primary")
                        clear = gr.Button("清空")
                
                # 右侧：工具状态
                with gr.Column(scale=1):
                    gr.Markdown("### 🔧 工具状态")
                    tool_status = gr.JSON(label="最近调用")
                    
                    gr.Markdown("### 💭 记忆")
                    memory_view = gr.JSON(label="相关记忆")
            
            # 事件绑定
            msg.submit(self.respond, [msg, chatbot], [msg, chatbot, tool_status])
            submit.click(self.respond, [msg, chatbot], [msg, chatbot, tool_status])
            clear.click(lambda: None, None, chatbot, queue=False)
        
        return demo
    
    async def respond(self, message, history):
        history.append([message, ""])
        
        # 调用 Agent
        response = await self.agent.handle(message)
        
        # 流式输出
        partial_message = ""
        for chunk in response:
            partial_message += chunk
            history[-1][1] = partial_message
            yield "", history, self.get_tool_status()
    
    def get_tool_status(self):
        return self.agent.get_recent_tool_calls()

if __name__ == "__main__":
    ui = GradioUI()
    demo = ui.create_interface()
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
```

---

## 推荐方案 C: Chainlit (AI 专用)

专为 AI Agent 设计的框架，内置很多有用功能。

```python
# ui_chainlit.py
import chainlit as cl
from miniclaw.core import MiniClawCore

@cl.on_chat_start
async def start():
    """初始化会话"""
    agent = MiniClawCore()
    cl.user_session.set("agent", agent)
    
    await cl.Message(
        content="你好！我是 🦞 小小龙虾，有什么可以帮你的？"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """处理用户消息"""
    agent = cl.user_session.get("agent")
    
    # 创建工具调用跟踪
    tool_calls = []
    
    # 处理消息
    msg = cl.Message(content="")
    await msg.send()
    
    async for chunk in agent.handle_stream(message.content):
        if chunk.type == "text":
            await msg.stream_token(chunk.content)
        elif chunk.type == "tool_call":
            # 显示工具调用
            async with cl.Step(name=chunk.tool_name, type="tool") as step:
                step.input = chunk.parameters
                tool_calls.append(step)
        elif chunk.type == "tool_result":
            # 更新工具结果
            if tool_calls:
                tool_calls[-1].output = chunk.result
    
    await msg.update()

@cl.on_tool_call
async def on_tool_call(tool_call):
    """工具调用钩子"""
    return await tool_call.run()
```

---

## 最终推荐

### 阶段一：快速验证
使用 **Gradio**，30 分钟搭出可用界面

### 阶段二：产品迭代
迁移到 **Next.js + React**，支持：
- 多用户会话
- 实时协作
- 插件市场
- 工作流编辑器

### 阶段三：高级功能
- **Canvas 模式**：支持拖拽文件、图片
- **MCP 集成**：Model Context Protocol 可视化
- **A2A 协议**：Agent-to-Agent 通信界面

---

## 关键设计要点

1. **实时反馈**：工具调用状态要实时显示，不能让用户干等
2. **渐进披露**：复杂信息默认折叠，点击展开
3. **错误处理**：工具失败要清晰展示错误信息
4. **可扩展性**：UI 组件要支持插件注册新类型

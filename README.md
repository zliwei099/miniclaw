# MiniClaw - 小小龙虾

## 项目结构

```
miniclaw/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── core/     # 核心引擎
│   │   ├── tools/    # 工具系统
│   │   ├── memory/   # 记忆系统
│   │   ├── llm/      # LLM 接口
│   │   └── api/      # API 路由
│   ├── data/         # 数据存储
│   └── requirements.txt
├── frontend/         # Next.js 前端
│   ├── app/          # App Router
│   ├── components/   # React 组件
│   ├── hooks/        # 自定义 Hooks
│   └── lib/          # 工具函数
└── shared/           # 共享类型定义
```

## 快速开始

### 1. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 启动服务
python main.py
```

后端运行在 http://localhost:8000

### 2. 启动前端

```bash
cd frontend
npm install

# 配置环境变量
cp .env.example .env.local

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:3000

### 3. 访问

打开浏览器访问 http://localhost:3000

## 功能特性

- ✅ WebSocket 实时通信
- ✅ 流式消息输出
- ✅ 工具调用可视化（实时状态展示）
- ✅ 内置工具：文件读写、命令执行、网页获取、目录列出
- ✅ 双层记忆系统（短期+长期）
- ✅ LLM 决策引擎（自动判断是否需要工具）

## 待实现

- [ ] 会话历史管理
- [ ] 工具自动生成
- [ ] 自我代码改进
- [ ] 工作流编辑器
- [ ] 插件系统

## 技术栈

**后端：**
- Python 3.11+
- FastAPI + WebSocket
- SQLite（可扩展 PostgreSQL）
- OpenAI API（可扩展多模型）

**前端：**
- Next.js 14 (App Router)
- React 18 + TypeScript
- Tailwind CSS
- Zustand（状态管理）

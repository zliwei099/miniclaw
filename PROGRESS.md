# MiniClaw 项目进展看板

## 📊 总体进度

```
核心功能: [████████░░] 80%
可视化UI: [████████░░] 80%
自我进化: [░░░░░░░░░░] 0% (待开发)
DIY扩展:  [░░░░░░░░░░] 0% (待开发)
```

---

## ✅ 已完成 (Done)

### 后端核心
| 模块 | 功能 | 状态 | 文件 |
|------|------|------|------|
| 核心引擎 | 流式消息处理 | ✅ | `backend/app/core/engine.py` |
| WebSocket | 实时通信 | ✅ | `backend/app/api/websocket.py` |
| 工具系统 | 5个内置工具 | ✅ | `backend/app/tools/registry.py` |
| 记忆系统 | 双层记忆 | ✅ | `backend/app/memory/store.py` |
| LLM接口 | 决策引擎 | ✅ | `backend/app/llm/interface.py` |
| REST API | 会话/工具管理 | ✅ | `backend/app/api/routes.py` |

### 前端界面
| 组件 | 功能 | 状态 | 文件 |
|------|------|------|------|
| 聊天容器 | 消息状态管理 | ✅ | `frontend/components/chat/ChatContainer.tsx` |
| 消息列表 | 消息展示 | ✅ | `frontend/components/chat/MessageList.tsx` |
| 工具卡片 | 实时状态+展开 | ✅ | `frontend/components/chat/ToolCallCard.tsx` |
| 输入框 | 发送/换行 | ✅ | `frontend/components/chat/InputBox.tsx` |
| 侧边栏 | 会话/工具入口 | ✅ | `frontend/components/sidebar/Sidebar.tsx` |
| WebSocket Hook | 自动重连 | ✅ | `frontend/hooks/useWebSocket.ts` |

---

## 🚧 进行中 (In Progress)

| 功能 | 进度 | 说明 |
|------|------|------|
| 会话持久化 | 50% | 内存存储→SQLite |
| 超时优化 | 30% | 心跳检测、超时配置 |

---

## 📋 待开发 (Todo)

### 高优先级
- [ ] 会话历史持久化（存数据库而不是内存）
- [ ] WebSocket 心跳检测（防止连接假死）
- [ ] 文件上传/下载功能
- [ ] 错误处理优化

### 中优先级
- [ ] 工具自动生成（自然语言→代码）
- [ ] 向量检索（ChromaDB）
- [ ] 多模型切换（OpenAI/Claude/本地）

### 低优先级
- [ ] 工作流编辑器（React Flow）
- [ ] 插件热加载系统
- [ ] 用户认证
- [ ] 移动端适配

---

## 🐛 已知问题

| 问题 | 严重程度 | 状态 |
|------|----------|------|
| 会话仅存内存，重启丢失 | 中 | 待修复 |
| WebSocket 无心跳检测 | 低 | 待修复 |
| 无文件上传功能 | 低 | 待开发 |

---

## 📅 开发日志

### 2026-03-10
- ✅ 完成核心架构设计
- ✅ 实现后端 FastAPI + WebSocket
- ✅ 实现前端 Next.js + 聊天界面
- ✅ 完成工具调用可视化
- ✅ 创建项目文档

---

## 🔗 相关文档

- [架构设计](https://www.feishu.cn/docx/EuSCdqpAaoUj7dx3coRcQDQFncD)
- [实现报告](https://www.feishu.cn/docx/Yq8CdWhUkogIhnxnWu4cCXhenIb)

---

*最后更新：2026-03-10 17:00*

# 小小龙虾 (MiniClaw) 架构方案

## 核心理念
**渐进式进化**：从最小内核开始，通过自我编程能力逐步扩展功能。

## 阶段一：MVP 核心架构（2-3天实现）

### 1. 系统架构图
```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │  CLI    │  │ Web UI  │  │ IM Bot  │  │  API    │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
└───────┼────────────┼────────────┼────────────┼──────────┘
        │            │            │            │
        └────────────┴──────┬─────┴────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                  核心调度引擎 (Core)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  消息路由 → 意图识别 → 工具选择 → 执行 → 反馈      │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐  ┌──────▼──────┐
│   工具注册表   │   │    LLM 接口层    │  │   记忆系统   │
│  ┌──────────┐│   │ ┌─────────────┐ │  │ ┌─────────┐ │
│  │ 工具发现  ││   │ │ 多模型支持   │ │  │ │ 短期记忆 │ │
│  │ 动态加载  ││   │ │ OpenAI/本地 │ │  │ │ 长期记忆 │ │
│  │ 参数校验  ││   │ │ Claude/Other│ │  │ │ 向量检索 │ │
│  └──────────┘│   │ └─────────────┘ │  │ └─────────┘ │
└──────────────┘   └─────────────────┘  └─────────────┘
```

### 2. 核心模块设计

#### 2.1 内核模块 (mini_claw/core/)
```python
# 最小内核 - 约300行代码
class MiniClawCore:
    """
    核心调度器：接收输入，协调工具执行
    """
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.memory = Memory()
        self.llm = LLMInterface()
    
    async def handle(self, user_input: str, context: dict) -> Response:
        # 1. 检索相关记忆
        relevant_memories = await self.memory.retrieve(user_input)
        
        # 2. LLM 决策：是否需要工具？
        decision = await self.llm.decide(user_input, relevant_memories)
        
        # 3. 执行工具或对话
        if decision.requires_tool:
            result = await self.tool_registry.execute(
                decision.tool_name, 
                decision.parameters
            )
            return await self.llm.synthesize(result, user_input)
        else:
            return await self.llm.chat(user_input, relevant_memories)
```

#### 2.2 工具系统 (mini_claw/tools/)
```python
# 工具定义 - 声明式
@tool(
    name="file_read",
    description="读取文件内容",
    parameters={
        "path": {"type": "string", "description": "文件路径"},
        "limit": {"type": "integer", "optional": True}
    }
)
async def file_read(path: str, limit: int = 100) -> str:
    """读取文件工具实现"""
    pass

# 工具注册表 - 支持动态发现
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool_def: Tool):
        self.tools[tool_def.name] = tool_def
    
    def auto_discover(self, directory: str):
        """自动发现目录下的所有工具"""
        pass
```

#### 2.3 记忆系统 (mini_claw/memory/)
```python
class Memory:
    """
    双层记忆：短期（会话级）+ 长期（持久化）
    """
    def __init__(self):
        self.short_term = ConversationBuffer()  # 当前会话
        self.long_term = VectorStore()          # ChromaDB/SQLite
        self.working = WorkingMemory()          # 临时变量
    
    async def store(self, key: str, value: any, permanent: bool = False):
        if permanent:
            await self.long_term.store(key, value)
        else:
            self.short_term.add(key, value)
    
    async def retrieve(self, query: str, k: int = 5) -> List[MemoryItem]:
        return await self.long_term.similarity_search(query, k)
```

#### 2.4 LLM 接口层 (mini_claw/llm/)
```python
class LLMInterface:
    """
    统一LLM接口，支持多模型
    """
    def __init__(self, provider: str = "openai"):
        self.provider = self._load_provider(provider)
    
    async def decide(self, input: str, context: dict) -> Decision:
        """
        决策是否需要调用工具
        返回：Decision(tool_name, parameters, reasoning)
        """
        prompt = self._build_decision_prompt(input, context)
        response = await self.provider.complete(prompt)
        return self._parse_decision(response)
    
    async def chat(self, input: str, context: dict) -> str:
        """普通对话"""
        pass
```

---

## 阶段二：自我进化机制（核心亮点）

### 进化循环
```
用户需求/反馈
     ↓
分析问题 → 生成方案 → 验证测试 → 部署上线
     ↑                                  │
     └────── 监控效果 ← 收集反馈 ───────┘
```

### 具体进化能力

#### 1. 工具自我生成
```python
class ToolGenerator:
    """
    根据需求自动生成工具代码
    """
    async def generate_tool(self, requirement: str) -> Tool:
        # 1. 分析需求
        analysis = await self.llm.analyze(requirement)
        
        # 2. 生成代码
        code = await self.llm.generate_code(
            prompt=f"生成一个工具：{requirement}",
            template=TOOL_TEMPLATE,
            constraints=["类型安全", "错误处理", "文档注释"]
        )
        
        # 3. 验证代码
        if await self.validator.check(code):
            return self.register_tool(code)
        else:
            # 自修复
            return await self.fix_and_retry(code)
```

#### 2. 自我代码改进
```python
class SelfImprover:
    """
    分析自身代码，提出改进建议
    """
    async def review_codebase(self):
        """定期自我审查"""
        issues = await self.find_issues()
        for issue in issues:
            fix = await self.generate_fix(issue)
            await self.create_pr(fix)
    
    async def learn_from_execution(self, task_result: Result):
        """从执行结果学习"""
        if task_result.failed:
            # 分析失败原因，改进处理逻辑
            await self.update_error_handling(task_result)
```

#### 3. 技能进化
```yaml
# skills/web_search/skill.yaml
name: web_search
version: 1.0.0
auto_evolve: true  # 启用自动进化

evolution_rules:
  - trigger: "搜索失败率 > 20%"
    action: "优化搜索策略"
  - trigger: "用户抱怨结果质量"
    action: "改进结果排序算法"
  - trigger: "新搜索API出现"
    action: "集成新API并A/B测试"
```

---

## 阶段三：DIY 扩展系统

### 1. 插件架构
```
plugins/
├── my_custom_tool/
│   ├── __init__.py
│   ├── tool.py          # 工具实现
│   ├── test_tool.py     # 自动化测试
│   └── manifest.yaml    # 元数据
└── my_workflow/
    ├── __init__.py
    ├── workflow.py      # 工作流定义
    └── triggers.yaml    # 触发条件
```

### 2. 自然语言扩展
```python
# 用户可以通过对话创建工具
user: "帮我创建一个工具，可以查询天气并发送邮件提醒"

# 系统自动：
# 1. 分析需求
# 2. 生成代码
# 3. 创建测试
# 4. 注册到系统
# 5. 返回使用方式
```

### 3. 可视化工作流编辑器
```
┌────────────────────────────────────────┐
│  [触发器] ──→ [条件判断] ──→ [动作1]  │
│                  │                     │
│                  ↓                     │
│              [动作2]                   │
└────────────────────────────────────────┘
```

---

## 技术选型建议

| 组件 | 推荐方案 | 备选方案 |
|------|----------|----------|
| 语言 | Python 3.11+ | TypeScript (Node) |
| 框架 | FastAPI + async | Flask + Celery |
| 数据库 | SQLite (轻量) | PostgreSQL |
| 向量库 | ChromaDB | Weaviate |
| 配置 | Pydantic + YAML | 纯JSON |
| 测试 | pytest | unittest |
| 部署 | Docker + docker-compose | 直接运行 |

---

## 实现路线图

### Week 1: 骨架搭建
- [ ] Day 1-2: 核心调度引擎 + 基础CLI
- [ ] Day 3-4: 工具系统 + 3个基础工具（文件、网页、执行）
- [ ] Day 5-7: LLM接口 + 记忆系统

### Week 2: 能力增强
- [ ] Day 8-9: Web UI (Gradio/Streamlit)
- [ ] Day 10-11: IM接入 (飞书/微信)
- [ ] Day 12-14: 自我进化原型

### Week 3: 进化系统
- [ ] Day 15-17: 工具自动生成
- [ ] Day 18-19: 代码自我改进
- [ ] Day 20-21: DIY插件系统

---

## 关键设计原则

1. **渐进式复杂** - 先让简单版本跑起来，再逐步加功能
2. **声明式优先** - 能用配置解决的，不写代码
3. **测试驱动** - 每个功能必须有自动化测试
4. **可观测性** - 全程日志，便于调试和学习
5. **安全沙箱** - 代码执行必须隔离，防止自我破坏

---

## 下一步

你觉得这个方向对吗？我们可以：
1. 细化某个模块的设计
2. 直接开始写代码（我可以帮你实现核心骨架）
3. 调整架构方向

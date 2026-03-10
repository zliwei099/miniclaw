"""
LLM 接口层
"""
import os
import json
from typing import Any, Dict, List, Optional


class LLMInterface:
    """
    统一 LLM 接口，支持多模型
    """
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # 工具描述（用于提示词）
        self.tools_description = self._build_tools_description()
    
    def _build_tools_description(self) -> str:
        """构建工具描述"""
        tools = [
            {
                "name": "file_read",
                "description": "读取文件内容",
                "parameters": {"path": "文件路径", "limit": "可选，最大行数"}
            },
            {
                "name": "file_write",
                "description": "写入文件内容",
                "parameters": {"path": "文件路径", "content": "文件内容"}
            },
            {
                "name": "execute_command",
                "description": "执行 shell 命令",
                "parameters": {"command": "命令", "timeout": "可选，超时秒数"}
            },
            {
                "name": "web_fetch",
                "description": "获取网页内容",
                "parameters": {"url": "网页URL"}
            },
            {
                "name": "list_directory",
                "description": "列出目录内容",
                "parameters": {"path": "目录路径"}
            }
        ]
        
        return json.dumps(tools, indent=2, ensure_ascii=False)
    
    async def decide(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        决策是否需要调用工具
        返回: {"requires_tool": bool, "tool_name": str, "parameters": dict}
        """
        # 构建决策提示词
        prompt = f"""你是一个AI助手，需要判断是否需要调用工具来完成用户请求。

可用工具：
{self.tools_description}

用户输入：{user_input}

请分析用户请求，判断是否需要调用工具。
如果需要工具，请返回 JSON 格式：
{{
    "requires_tool": true,
    "tool_name": "工具名称",
    "parameters": {{参数}},
    "reasoning": "简要说明为什么选择这个工具"
}}

如果不需要工具（只是普通对话），请返回：
{{
    "requires_tool": false,
    "reasoning": "简要说明为什么不需要工具"
}}

只返回 JSON，不要其他内容。"""
        
        try:
            # 调用 LLM
            response = await self._call_llm(prompt)
            
            # 解析 JSON
            # 提取 JSON 部分（防止模型输出额外文本）
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                decision = json.loads(json_str)
            else:
                decision = {"requires_tool": False}
            
            return decision
            
        except Exception as e:
            print(f"[LLM] 决策失败: {e}")
            return {"requires_tool": False}
    
    async def chat(
        self, 
        user_input: str, 
        context: Dict[str, Any]
    ) -> str:
        """
        普通对话
        """
        # 构建对话提示词
        memories = context.get("memories", [])
        history = context.get("conversation_history", [])
        
        memory_text = "\n".join([
            f"- {m.get('content', '')}" 
            for m in memories[:3]
        ]) if memories else "无相关记忆"
        
        history_text = "\n".join([
            f"{h.get('role', 'user')}: {h.get('content', '')}"
            for h in history[-5:]
        ]) if history else "无历史对话"
        
        prompt = f"""你是一个有帮助的AI助手。

相关记忆：
{memory_text}

历史对话：
{history_text}

用户：{user_input}

助手："""
        
        return await self._call_llm(prompt)
    
    async def synthesize(
        self, 
        user_input: str,
        tool_result: Any,
        context: Dict[str, Any]
    ) -> str:
        """
        基于工具结果生成回复
        """
        prompt = f"""你是一个有帮助的AI助手。用户提出了一个请求，你已经使用工具获取了结果，现在需要基于结果给出回复。

用户请求：{user_input}

工具执行结果：
{json.dumps(tool_result, ensure_ascii=False, indent=2)}

请基于以上结果，给用户一个清晰、有帮助的回复。如果结果是错误或空，请礼貌地告知用户。"""
        
        return await self._call_llm(prompt)
    
    async def _call_llm(self, prompt: str) -> str:
        """
        调用 LLM API
        """
        if not self.api_key:
            # 模拟响应（用于测试）
            return self._mock_response(prompt)
        
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个有帮助的AI助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[LLM] API 调用失败: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """
        模拟 LLM 响应（用于测试）
        """
        # 简单的关键词匹配来决定是否调用工具
        tool_keywords = {
            "file_read": ["读取文件", "查看文件", "打开文件", "read file"],
            "file_write": ["写入文件", "保存文件", "创建文件", "write file"],
            "execute_command": ["执行命令", "运行命令", "执行", "run command"],
            "web_fetch": ["获取网页", "抓取网页", "fetch", "网页内容"],
            "list_directory": ["列出目录", "查看目录", "目录内容", "list files"]
        }
        
        prompt_lower = prompt.lower()
        
        for tool_name, keywords in tool_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                # 提取可能的参数（简单实现）
                parameters = {}
                
                if tool_name == "file_read":
                    parameters = {"path": "./example.txt"}
                elif tool_name == "list_directory":
                    parameters = {"path": "."}
                elif tool_name == "execute_command":
                    parameters = {"command": "ls -la"}
                elif tool_name == "web_fetch":
                    parameters = {"url": "https://example.com"}
                
                return json.dumps({
                    "requires_tool": True,
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "reasoning": f"用户提到了{tool_name}相关操作"
                }, ensure_ascii=False)
        
        # 默认不调用工具
        return json.dumps({
            "requires_tool": False,
            "reasoning": "用户请求是普通对话，不需要调用工具"
        }, ensure_ascii=False)

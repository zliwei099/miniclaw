"""
工具注册表
"""
import os
import sys
import json
import asyncio
import importlib
import inspect
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: List[ToolParameter]
    handler: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required
                }
                for p in self.parameters
            ]
        }


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()
    
    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"[ToolRegistry] 已注册工具: {tool.name}")
    
    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """列出所有工具"""
        return list(self.tools.values())
    
    async def execute(self, name: str, parameters: Dict[str, Any]) -> Any:
        """执行工具"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"未知工具: {name}")
        
        if not tool.handler:
            raise ValueError(f"工具 {name} 没有处理函数")
        
        # 调用处理函数
        if asyncio.iscoroutinefunction(tool.handler):
            return await tool.handler(**parameters)
        else:
            return tool.handler(**parameters)
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        # 1. 文件读取工具
        self.register(Tool(
            name="file_read",
            description="读取文件内容",
            parameters=[
                ToolParameter("path", "string", "文件路径", True),
                ToolParameter("limit", "integer", "最大读取行数", False)
            ],
            handler=self._file_read
        ))
        
        # 2. 文件写入工具
        self.register(Tool(
            name="file_write",
            description="写入文件内容",
            parameters=[
                ToolParameter("path", "string", "文件路径", True),
                ToolParameter("content", "string", "文件内容", True)
            ],
            handler=self._file_write
        ))
        
        # 3. 执行命令工具
        self.register(Tool(
            name="execute_command",
            description="执行 shell 命令",
            parameters=[
                ToolParameter("command", "string", "要执行的命令", True),
                ToolParameter("timeout", "integer", "超时时间(秒)", False)
            ],
            handler=self._execute_command
        ))
        
        # 4. 网页获取工具
        self.register(Tool(
            name="web_fetch",
            description="获取网页内容",
            parameters=[
                ToolParameter("url", "string", "网页URL", True)
            ],
            handler=self._web_fetch
        ))
        
        # 5. 列出目录工具
        self.register(Tool(
            name="list_directory",
            description="列出目录内容",
            parameters=[
                ToolParameter("path", "string", "目录路径", True)
            ],
            handler=self._list_directory
        ))
    
    # ===== 内置工具处理函数 =====
    
    def _file_read(self, path: str, limit: int = 100) -> str:
        """读取文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:limit]
                return ''.join(lines)
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    def _file_write(self, path: str, content: str) -> str:
        """写入文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件已写入: {path}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"
    
    async def _execute_command(self, command: str, timeout: int = 30) -> str:
        """执行命令"""
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), 
                timeout=timeout
            )
            
            result = stdout.decode('utf-8', errors='ignore')
            if stderr:
                result += f"\n[错误输出]\n{stderr.decode('utf-8', errors='ignore')}"
            
            return result
        except asyncio.TimeoutError:
            return f"命令执行超时 ({timeout}秒)"
        except Exception as e:
            return f"命令执行失败: {str(e)}"
    
    async def _web_fetch(self, url: str) -> str:
        """获取网页"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    return await response.text()
        except Exception as e:
            return f"获取网页失败: {str(e)}"
    
    def _list_directory(self, path: str = ".") -> List[Dict[str, Any]]:
        """列出目录"""
        try:
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(full_path) else "file",
                    "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None
                })
            return items
        except Exception as e:
            return [{"error": str(e)}]

"""
MiniClaw Core - 核心调度引擎
"""
import uuid
import json
from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime

from app.tools.registry import ToolRegistry
from app.memory.store import MemoryStore
from app.llm.interface import LLMInterface
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..'))
from shared.types import (
    Message, MessageRole, ToolCall, ToolStatus,
    AgentRequest, AgentResponse, Conversation
)


class MiniClawCore:
    """
    核心调度器：接收输入，协调工具执行
    """
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.memory = MemoryStore()
        self.llm = LLMInterface()
        self.conversations: Dict[str, Conversation] = {}
    
    async def process_message(
        self, 
        request: AgentRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        处理用户消息，返回流式响应
        """
        # 获取或创建会话
        conversation_id = request.conversation_id or str(uuid.uuid4())
        conversation = self._get_or_create_conversation(conversation_id)
        
        # 添加用户消息
        user_message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content=request.message
        )
        conversation.messages.append(user_message)
        
        # 检索相关记忆
        relevant_memories = await self.memory.retrieve(request.message, k=5)
        context = {
            "memories": relevant_memories,
            "conversation_history": [
                {"role": m.role.value, "content": m.content}
                for m in conversation.messages[-10:]  # 最近10条
            ]
        }
        
        # 生成 assistant 消息
        assistant_message_id = str(uuid.uuid4())
        yield {
            "type": "assistant_start",
            "data": {"id": assistant_message_id, "conversation_id": conversation_id}
        }
        
        # 调用 LLM 决策
        decision = await self.llm.decide(request.message, context)
        
        if decision.get("requires_tool"):
            # 需要调用工具
            tool_name = decision["tool_name"]
            parameters = decision["parameters"]
            
            # 创建工具调用
            tool_call = ToolCall(
                id=str(uuid.uuid4()),
                name=tool_name,
                parameters=parameters,
                status=ToolStatus.PENDING
            )
            
            yield {
                "type": "tool_call",
                "data": {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "parameters": tool_call.parameters,
                    "status": tool_call.status.value
                }
            }
            
            # 执行工具
            tool_call.status = ToolStatus.RUNNING
            try:
                result = await self.tool_registry.execute(tool_name, parameters)
                tool_call.status = ToolStatus.COMPLETED
                tool_call.result = result
                tool_call.completed_at = datetime.now()
                
                yield {
                    "type": "tool_result",
                    "data": {
                        "tool_call_id": tool_call.id,
                        "status": tool_call.status.value,
                        "result": result
                    }
                }
                
                # 基于工具结果生成回复
                response_content = await self.llm.synthesize(
                    request.message, 
                    result,
                    context
                )
                
            except Exception as e:
                tool_call.status = ToolStatus.ERROR
                tool_call.error = str(e)
                tool_call.completed_at = datetime.now()
                
                yield {
                    "type": "tool_result",
                    "data": {
                        "tool_call_id": tool_call.id,
                        "status": tool_call.status.value,
                        "error": str(e)
                    }
                }
                
                response_content = f"工具执行出错: {str(e)}"
        else:
            # 普通对话
            response_content = await self.llm.chat(request.message, context)
        
        # 流式输出回复
        for chunk in self._stream_text(response_content):
            yield {
                "type": "stream_chunk",
                "data": {"content": chunk}
            }
        
        # 完成响应
        yield {
            "type": "assistant_end",
            "data": {
                "id": assistant_message_id,
                "content": response_content,
                "conversation_id": conversation_id
            }
        }
        
        # 保存 assistant 消息到会话
        assistant_message = Message(
            id=assistant_message_id,
            role=MessageRole.ASSISTANT,
            content=response_content
        )
        conversation.messages.append(assistant_message)
        conversation.updated_at = datetime.now()
        
        # 保存到长期记忆
        await self.memory.store(
            f"user: {request.message}\nassistant: {response_content}",
            metadata={"conversation_id": conversation_id}
        )
    
    def _get_or_create_conversation(self, conversation_id: str) -> Conversation:
        """获取或创建会话"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(
                id=conversation_id
            )
        return self.conversations[conversation_id]
    
    def _stream_text(self, text: str, chunk_size: int = 10) -> List[str]:
        """将文本分块，模拟流式输出"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i+chunk_size])
        return chunks
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        return self.conversations.get(conversation_id)
    
    def list_conversations(self) -> List[Conversation]:
        """列出所有会话"""
        return list(self.conversations.values())

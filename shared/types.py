# MiniClaw 共享类型定义

from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ToolCall:
    """工具调用定义"""
    id: str
    name: str
    parameters: Dict[str, Any]
    status: ToolStatus = ToolStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Message:
    """消息定义"""
    id: str
    role: MessageRole
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """会话定义"""
    id: str
    title: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ToolDefinition:
    """工具定义（用于注册和发现）"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Optional[str] = None  # 处理函数路径


@dataclass
class AgentRequest:
    """Agent 请求"""
    message: str
    conversation_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent 响应"""
    message: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    conversation_id: str = ""


# WebSocket 消息类型

class WSMessageType(Enum):
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STREAM_CHUNK = "stream_chunk"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


@dataclass
class WSMessage:
    """WebSocket 消息"""
    type: WSMessageType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

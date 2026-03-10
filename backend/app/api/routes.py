"""
API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.core.engine import MiniClawCore
from app.tools.registry import ToolRegistry

router = APIRouter()

# 全局核心实例
core = MiniClawCore()
tool_registry = ToolRegistry()


@router.post("/chat")
async def chat(request: Dict[str, Any]):
    """发送消息（非流式）"""
    message = request.get("message", "")
    conversation_id = request.get("conversation_id")
    
    if not message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 收集流式响应
    full_response = ""
    tool_calls = []
    final_conversation_id = conversation_id
    
    async for chunk in core.process_message(type('Request', (), {
        'message': message,
        'conversation_id': conversation_id,
        'context': {}
    })()):
        if chunk["type"] == "stream_chunk":
            full_response += chunk["data"]["content"]
        elif chunk["type"] == "tool_call":
            tool_calls.append(chunk["data"])
        elif chunk["type"] == "assistant_end":
            final_conversation_id = chunk["data"].get("conversation_id")
    
    return {
        "message": full_response,
        "tool_calls": tool_calls,
        "conversation_id": final_conversation_id
    }


@router.get("/conversations")
async def list_conversations():
    """列出所有会话"""
    conversations = core.list_conversations()
    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title or f"会话 {c.id[:8]}",
                "message_count": len(c.messages),
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in conversations
        ]
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取会话详情"""
    conversation = core.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "parameters": tc.parameters,
                        "status": tc.status.value,
                        "result": tc.result,
                        "error": tc.error
                    }
                    for tc in m.tool_calls
                ],
                "created_at": m.created_at.isoformat()
            }
            for m in conversation.messages
        ],
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat()
    }


@router.get("/tools")
async def list_tools():
    """列出所有可用工具"""
    tools = tool_registry.list_tools()
    return {
        "tools": [tool.to_dict() for tool in tools]
    }


@router.post("/tools/execute")
async def execute_tool(request: Dict[str, Any]):
    """执行工具"""
    tool_name = request.get("name")
    parameters = request.get("parameters", {})
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="工具名称不能为空")
    
    try:
        result = await tool_registry.execute(tool_name, parameters)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

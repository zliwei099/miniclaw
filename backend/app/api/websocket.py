"""
WebSocket 处理
"""
import json
from fastapi import WebSocket, WebSocketDisconnect

from app.core.engine import MiniClawCore
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..'))
from shared.types import AgentRequest

# 全局核心实例
core = MiniClawCore()


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] 新连接，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WebSocket] 连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 处理入口"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "无效的 JSON 格式"}
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_message(websocket: WebSocket, message: dict):
    """处理 WebSocket 消息"""
    msg_type = message.get("type")
    
    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})
        return
    
    if msg_type == "user_message":
        content = message.get("content", "")
        conversation_id = message.get("conversation_id")
        
        if not content:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "消息内容不能为空"}
            })
            return
        
        # 创建请求对象
        request = AgentRequest(
            message=content,
            conversation_id=conversation_id,
            context={}
        )
        
        # 处理消息并流式返回
        async for chunk in core.process_message(request):
            await websocket.send_json(chunk)
        
        return
    
    if msg_type == "get_conversations":
        conversations = core.list_conversations()
        await websocket.send_json({
            "type": "conversations_list",
            "data": {
                "conversations": [
                    {
                        "id": c.id,
                        "title": c.title or f"会话 {c.id[:8]}",
                        "message_count": len(c.messages),
                        "created_at": c.created_at.isoformat()
                    }
                    for c in conversations
                ]
            }
        })
        return
    
    # 未知消息类型
    await websocket.send_json({
        "type": "error",
        "data": {"message": f"未知消息类型: {msg_type}"}
    })

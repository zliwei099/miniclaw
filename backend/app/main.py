"""
FastAPI 主应用
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import router as api_router
from app.api.websocket import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🦞 MiniClaw 启动中...")
    yield
    print("🦞 MiniClaw 关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="MiniClaw API",
    description="小小龙虾 - 渐进式 AI Agent",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")

# WebSocket 路由
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket_endpoint(websocket)


@app.get("/")
async def root():
    return {
        "name": "MiniClaw",
        "version": "0.1.0",
        "description": "小小龙虾 - 渐进式 AI Agent"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

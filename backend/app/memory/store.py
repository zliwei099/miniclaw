"""
记忆系统
"""
import os
import json
import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


class MemoryStore:
    """
    双层记忆系统：短期（内存）+ 长期（SQLite + 可选向量存储）
    """
    
    def __init__(self, db_path: str = "./data/memory.db"):
        self.db_path = db_path
        self.short_term: List[Dict[str, Any]] = []  # 短期记忆（当前会话）
        self.max_short_term = 100
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    async def store(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        存储记忆
        """
        # 短期记忆
        self.short_term.append({
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制短期记忆大小
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]
        
        # 长期记忆
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memories (content, metadata) VALUES (?, ?)",
                (content, json.dumps(metadata or {}))
            )
            conn.commit()
    
    async def retrieve(
        self, 
        query: str, 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索相关记忆
        简单实现：基于关键词匹配
        """
        results = []
        
        # 从短期记忆中搜索
        for memory in reversed(self.short_term):
            if self._is_relevant(query, memory["content"]):
                results.append(memory)
                if len(results) >= k:
                    return results
        
        # 从长期记忆中搜索
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT content, metadata, created_at FROM memories ORDER BY created_at DESC LIMIT ?",
                (k * 2,)  # 多取一些用于过滤
            )
            
            for row in cursor.fetchall():
                content, metadata, created_at = row
                if self._is_relevant(query, content):
                    results.append({
                        "content": content,
                        "metadata": json.loads(metadata or '{}'),
                        "timestamp": created_at
                    })
                    if len(results) >= k:
                        break
        
        return results[:k]
    
    def _is_relevant(self, query: str, content: str) -> bool:
        """
        简单相关性判断（基于关键词匹配）
        后续可以升级为向量相似度
        """
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # 计算重叠度
        if not query_words:
            return False
        
        overlap = len(query_words & content_words)
        return overlap > 0
    
    async def get_conversation_history(
        self, 
        conversation_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取特定会话的历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT content, metadata, created_at 
                   FROM memories 
                   WHERE json_extract(metadata, '$.conversation_id') = ?
                   ORDER BY created_at DESC 
                   LIMIT ?""",
                (conversation_id, limit)
            )
            
            return [
                {
                    "content": row[0],
                    "metadata": json.loads(row[1] or '{}'),
                    "timestamp": row[2]
                }
                for row in cursor.fetchall()
            ]
    
    async def clear(self):
        """清空记忆"""
        self.short_term = []
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories")
            conn.commit()

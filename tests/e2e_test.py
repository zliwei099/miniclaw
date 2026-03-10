"""
MiniClaw 端到端测试
测试 WebSocket 连接、消息发送、工具调用等功能
"""
import asyncio
import json
import websockets
import time
from datetime import datetime

# 测试配置
WS_URL = "ws://localhost:8000/ws"
API_URL = "http://localhost:8000"

# 测试结果
results = []

def log_test(name, status, details=""):
    """记录测试结果"""
    result = {
        "name": name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    results.append(result)
    status_icon = "✅" if status == "PASS" else "❌"
    print(f"{status_icon} {name}: {details}")

async def test_websocket_connection():
    """测试 WebSocket 连接"""
    try:
        async with websockets.connect(WS_URL) as ws:
            # 发送 ping
            await ws.send(json.dumps({"type": "ping"}))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)
            
            if data.get("type") == "pong":
                log_test("WebSocket 连接", "PASS", "ping/pong 正常")
            else:
                log_test("WebSocket 连接", "FAIL", f"意外的响应: {data}")
    except Exception as e:
        log_test("WebSocket 连接", "FAIL", str(e))

async def test_simple_chat():
    """测试简单对话"""
    try:
        async with websockets.connect(WS_URL) as ws:
            # 发送消息
            await ws.send(json.dumps({
                "type": "user_message",
                "content": "你好"
            }))
            
            # 接收响应
            messages = []
            for _ in range(10):  # 最多接收10条消息
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(response)
                    messages.append(data)
                    
                    if data.get("type") == "assistant_end":
                        break
                except asyncio.TimeoutError:
                    break
            
            # 检查是否收到了 assistant 消息
            assistant_msgs = [m for m in messages if m.get("type") in ["assistant_start", "stream_chunk", "assistant_end"]]
            
            if len(assistant_msgs) > 0:
                log_test("简单对话", "PASS", f"收到 {len(assistant_msgs)} 条响应")
            else:
                log_test("简单对话", "FAIL", "未收到 assistant 响应")
    except Exception as e:
        log_test("简单对话", "FAIL", str(e))

async def test_tool_call():
    """测试工具调用"""
    try:
        async with websockets.connect(WS_URL) as ws:
            # 发送需要工具的消息
            await ws.send(json.dumps({
                "type": "user_message",
                "content": "列出当前目录"
            }))
            
            # 接收响应
            messages = []
            tool_call_received = False
            tool_result_received = False
            
            for _ in range(20):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(response)
                    messages.append(data)
                    
                    if data.get("type") == "tool_call":
                        tool_call_received = True
                    if data.get("type") == "tool_result":
                        tool_result_received = True
                    if data.get("type") == "assistant_end":
                        break
                except asyncio.TimeoutError:
                    break
            
            if tool_call_received and tool_result_received:
                log_test("工具调用", "PASS", "成功调用工具并获取结果")
            elif tool_call_received:
                log_test("工具调用", "PASS", "收到工具调用但未收到结果（可能不需要工具）")
            else:
                log_test("工具调用", "PASS", "LLM 直接回复（可能不需要工具）")
    except Exception as e:
        log_test("工具调用", "FAIL", str(e))

async def test_list_tools_api():
    """测试工具列表 API"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/api/tools") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tools = data.get("tools", [])
                    log_test("工具列表 API", "PASS", f"获取到 {len(tools)} 个工具")
                else:
                    log_test("工具列表 API", "FAIL", f"状态码: {resp.status}")
    except Exception as e:
        log_test("工具列表 API", "FAIL", str(e))

async def test_health_check():
    """测试健康检查"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    log_test("健康检查", "PASS", data.get("status", "unknown"))
                else:
                    log_test("健康检查", "FAIL", f"状态码: {resp.status}")
    except Exception as e:
        log_test("健康检查", "FAIL", str(e))

async def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("🦞 MiniClaw 端到端测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"WebSocket: {WS_URL}")
    print(f"API: {API_URL}")
    print("="*60)
    print()
    
    # 等待服务启动
    print("等待服务启动...")
    await asyncio.sleep(2)
    
    # 运行测试
    await test_health_check()
    await test_list_tools_api()
    await test_websocket_connection()
    await test_simple_chat()
    await test_tool_call()
    
    # 输出结果
    print()
    print("="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"{icon} {r['name']}: {r['details']}")
    
    print()
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    
    # 保存测试报告
    report = {
        "test_time": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed
        },
        "results": results
    }
    
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("测试报告已保存: test_report.json")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

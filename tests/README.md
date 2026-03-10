# MiniClaw 测试

## 端到端测试

运行测试前确保后端服务已启动：

```bash
cd backend
source venv/bin/activate
python main.py
```

然后在另一个终端运行测试：

```bash
cd tests
python e2e_test.py
```

## 测试覆盖

- ✅ WebSocket 连接 (ping/pong)
- ✅ 健康检查 API
- ✅ 工具列表 API
- ✅ 简单对话
- ✅ 工具调用流程

## 测试报告

测试完成后会生成 `test_report.json`，包含详细的测试结果和时间戳。

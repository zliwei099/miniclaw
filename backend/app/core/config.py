"""
WebSocket 配置
"""

# 心跳检测配置
HEARTBEAT_INTERVAL = 30  # 秒，发送 ping 的间隔
HEARTBEAT_TIMEOUT = 10   # 秒，等待 pong 的超时时间

# 连接配置
WS_PING_INTERVAL = 30    # 秒
WS_PONG_TIMEOUT = 10     # 秒

# 消息处理超时
MESSAGE_TIMEOUT = 300    # 秒，单条消息处理最大时间

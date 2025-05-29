import asyncio
import websockets
import json
from typing import Dict, Set

# 存儲所有活動的連接
connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}

async def register(websocket: websockets.WebSocketServerProtocol, game_type: str):
    """註冊新的WebSocket連接"""
    if game_type not in connections:
        connections[game_type] = set()
    connections[game_type].add(websocket)

async def unregister(websocket: websockets.WebSocketServerProtocol, game_type: str):
    """取消註冊WebSocket連接"""
    connections[game_type].remove(websocket)
    if not connections[game_type]:
        del connections[game_type]

async def broadcast(game_type: str, message: dict):
    """向指定遊戲類型的所有連接廣播消息"""
    if game_type in connections:
        message_str = json.dumps(message)
        await asyncio.gather(
            *[ws.send(message_str) for ws in connections[game_type]]
        )

async def handler(websocket: websockets.WebSocketServerProtocol, path: str):
    """處理WebSocket連接"""
    # 從路徑中提取遊戲類型
    game_type = path.split('/')[1]  # 例如: /roulette/123 -> roulette
    
    try:
        await register(websocket, game_type)
        async for message in websocket:
            try:
                data = json.loads(message)
                # 處理消息並廣播
                await broadcast(game_type, {
                    "type": "message",
                    "data": data
                })
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "error": "Invalid JSON format"
                }))
    finally:
        await unregister(websocket, game_type)

async def main():
    """啟動WebSocket服務器"""
    server = await websockets.serve(
        handler,
        "localhost",
        8765,
        path="/ws"
    )
    print("WebSocket server started on ws://localhost:8765/ws")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 
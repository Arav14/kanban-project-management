import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket
import redis.asyncio as aioredis
from app.core.config import settings

class ConnectionManager:
    """
    Manages Websocket connections per board.
    Uses Redis Pub/Sub to broadcast events aross multiple server instances
    """

    def __init__(self):
        # board.id -> set of connected websockets
        self.connections: Dict[int, Set[WebSocket]] = {}
        self.redis: aioredis.Redis = None

    async def startup(self):
        self.redis = await aioredis.from_url(settings.REDIS_URL, decode_responses = True)
        # Start listening to Redis channel in background
        asyncio.create_task(self._redis_listener())

    async def connect(self, websocket: WebSocket, board_id: int):
        await websocket.accept()
        if board_id not in self.connections:
            self.connections[board_id] = set()
        self.connections[board_id].add(websocket)

    def disconnect(self, websocket: WebSocket, board_id: int):
        if board_id not in self.connections:
            self.connections[board_id].discard(websocket)

    async def broadcast(self, board_id: int, event: dict):
        # Publish event to Redis - all server instances will pick it up
        payload = json.dumps({"board_id": board_id, "event": event})
        await self.redis.publish("kanban:events", payload)

    async def _redis_listener(self):
        # Subscribe to Redis and forward messages to local WebSocket clients
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("kanban:events")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                data = json.loads(message["data"])
                board_id = data["board_id"]
                event = data["event"]
                await self._send_to_board(board_id, event)
            except Exception:
                pass

    async def _send_to_board(self, board_id: int, event: dict):
        # Send event to all WebSocket clients on this board.
        clients = self.connections.get(board_id, set()).copy()
        dead = set()
        for ws in clients:
            try:
                await ws.send_json(event)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.connections[board_id].discard(ws)

manager = ConnectionManager()

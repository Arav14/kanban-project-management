import asyncio
import json
import logging

import redis.asyncio as aioredis
from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections per board and broadcast through Redis."""

    def __init__(self) -> None:
        self.connections: dict[int, set[WebSocket]] = {}
        self.redis: aioredis.Redis | None = None
        self._listener_task: asyncio.Task | None = None

    async def startup(self) -> None:
        if self.redis is not None:
            return

        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

        self._listener_task = asyncio.create_task(
            self._redis_listener()
        )

    async def shutdown(self) -> None:
        if self._listener_task is not None:
            self._listener_task.cancel()

            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

            self._listener_task = None

        if self.redis is not None:
            await self.redis.aclose()
            self.redis = None

    async def connect(
        self,
        websocket: WebSocket,
        board_id: int,
    ) -> None:
        await websocket.accept()

        self.connections.setdefault(
            board_id,
            set(),
        ).add(websocket)

    def disconnect(
        self,
        websocket: WebSocket,
        board_id: int,
    ) -> None:
        clients = self.connections.get(board_id)

        if clients is None:
            return

        clients.discard(websocket)

        if not clients:
            self.connections.pop(board_id, None)

    async def broadcast(
        self,
        board_id: int,
        event: dict,
    ) -> None:
        if self.redis is None:
            return

        payload = json.dumps(
            {
                "board_id": board_id,
                "event": event,
            }
        )

        await self.redis.publish(
            "kanban:events",
            payload,
        )

    async def _redis_listener(self) -> None:
        if self.redis is None:
            return

        pubsub = self.redis.pubsub()

        await pubsub.subscribe(
            "kanban:events"
        )

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(
                        message["data"]
                    )

                    await self._send_to_board(
                        data["board_id"],
                        data["event"],
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                    json.JSONDecodeError,
                ):
                    logger.exception(
                        "Invalid Redis event payload"
                    )

        finally:
            await pubsub.unsubscribe(
                "kanban:events"
            )
            await pubsub.aclose()

    async def _send_to_board(
        self,
        board_id: int,
        event: dict,
    ) -> None:
        clients = (
            self.connections
            .get(board_id, set())
            .copy()
        )

        dead: set[WebSocket] = set()

        for websocket in clients:
            try:
                await websocket.send_json(event)
            except Exception:
                logger.exception(
                    "Failed to send WebSocket event"
                )
                dead.add(websocket)

        for websocket in dead:
            self.disconnect(
                websocket,
                board_id,
            )


manager = ConnectionManager()

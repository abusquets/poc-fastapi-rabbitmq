from typing import List

from fastapi import WebSocket

from app.schemas import BCMessageDTO


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: BCMessageDTO) -> None:
        for connection in self.active_connections:
            await connection.send_text(message.model_dump_json())

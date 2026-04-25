from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from application.schemas.user_schema import UserSchema
from application.services.chat_service import ChatService
from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from entrypoints.dependencies import get_uow, get_ws_authenticated_user

router = APIRouter(tags=["ws"])


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = {}

    async def connect(self, chat_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._rooms.setdefault(chat_id, set()).add(ws)

    def disconnect(self, chat_id: int, ws: WebSocket) -> None:
        room = self._rooms.get(chat_id)
        if not room:
            return
        room.discard(ws)
        if not room:
            self._rooms.pop(chat_id, None)

    async def broadcast(self, chat_id: int, message: dict) -> None:
        room = self._rooms.get(chat_id, set()).copy()
        for ws in room:
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(chat_id, ws)


manager = ConnectionManager()


@router.websocket("/ws/chat/{chat_id}")
async def ws_chat(
    chat_id: int,
    websocket: WebSocket,
    user: UserSchema = Depends(get_ws_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    async with uow:
        if user.id is None or not await uow.chat_repo.is_member(chat_id, user.id):
            await websocket.close(code=1008)
            return

    await manager.connect(chat_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "text":
                dto = await ChatService(uow).create_text_message(user=user, chat_id=chat_id, text=data.get("text"))
                await manager.broadcast(chat_id, dto.model_dump())
            elif msg_type == "audio":
                dto = await ChatService(uow).create_audio_message(
                    user=user, chat_id=chat_id, audio_key=data.get("audio_key")
                )
                await manager.broadcast(chat_id, dto.model_dump())
            else:
                await websocket.send_json({"error": "Unknown message type"})
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
        return
    except Exception:
        manager.disconnect(chat_id, websocket)
        await websocket.close(code=1011)
        return

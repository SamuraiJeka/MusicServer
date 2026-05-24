from __future__ import annotations

from fastapi import WebSocket

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork


class MessengerConnectionManager:
    """Одно WS-подключение на пользователя (как в типичном мессенджере)."""

    def __init__(self) -> None:
        self._by_user: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._by_user.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self._by_user.get(user_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            self._by_user.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        conns = self._by_user.get(user_id, set()).copy()
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(user_id, ws)


messenger_manager = MessengerConnectionManager()


async def push_chat_message(uow: SqlAlchemyUnitOfWork, chat_id: int, message: dict) -> None:
    async with uow:
        member_ids = await uow.chat_repo.list_member_user_ids(chat_id)

    envelope = {"event": "message", "message": message}
    for user_id in member_ids:
        await messenger_manager.send_to_user(user_id, envelope)

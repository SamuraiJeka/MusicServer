from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from entrypoints.dependencies import authenticate_websocket, get_uow
from entrypoints.messenger_connection_manager import messenger_manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws/messenger")
async def ws_messenger(
    websocket: WebSocket,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> None:
    user = await authenticate_websocket(websocket, uow)
    if user is None or user.id is None:
        return

    user_id = user.id
    await messenger_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        messenger_manager.disconnect(user_id, websocket)
    except Exception:
        messenger_manager.disconnect(user_id, websocket)
        await websocket.close(code=1011)

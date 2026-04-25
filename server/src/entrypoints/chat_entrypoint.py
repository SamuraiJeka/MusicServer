from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.exceptions import ApplicationError
from application.schemas.chat_schemas import ChatSchema, MessageHistorySchema, UploadAudioResponseSchema
from application.schemas.user_schema import UserSchema
from application.services.chat_service import ChatService
from entrypoints.dependencies import get_authenticated_user, get_uow

router = APIRouter(tags=["chat"])


@router.post("/chats/{user_id}", response_model=ChatSchema)
async def create_or_get_private_chat(
    user_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> ChatSchema:
    try:
        return await ChatService(uow).get_or_create_private_chat(user=user, other_user_id=user_id)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/chats", response_model=list[ChatSchema])
async def list_my_chats(
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[ChatSchema]:
    return await ChatService(uow).list_my_chats(user)


@router.get("/messages/{chat_id}", response_model=MessageHistorySchema)
async def get_message_history(
    chat_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> MessageHistorySchema:
    try:
        return await ChatService(uow).list_messages(user=user, chat_id=chat_id, limit=limit, offset=offset)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/upload/audio", response_model=UploadAudioResponseSchema)
async def upload_audio(
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> UploadAudioResponseSchema:
    try:
        content = await file.read()
        key = await ChatService(uow).upload_audio(user=user, content=content, original_filename=file.filename)
        return UploadAudioResponseSchema(audio_key=key)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e

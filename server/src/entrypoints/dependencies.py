import jwt
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from domain.ports.uow_interface import UoWInterface
from adapters.postgres.engine import get_session
from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.schemas.user_schema import UserSchema
from application.services.user_service import UserService

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> UoWInterface:
    return SqlAlchemyUnitOfWork(session)


async def get_authenticated_user(
    token: str = Depends(oauth2_schema),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> UserSchema:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            raise credentials_exception
        
        email = payload.get("email")
        if not email:
            raise credentials_exception
        
        return await UserService(uow).get_by_email(email)

    except jwt.exceptions.ExpiredSignatureError:
        raise expired_token_exception
    except jwt.exceptions.PyJWTError:
        raise credentials_exception


async def authenticate_websocket(
    websocket: WebSocket,
    uow: SqlAlchemyUnitOfWork,
) -> UserSchema | None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            await websocket.close(code=1008, reason="Invalid token type")
            return None
        email = payload.get("email")
        if not email:
            await websocket.close(code=1008, reason="Invalid token payload")
            return None
        return await UserService(uow).get_by_email(email)
    except jwt.exceptions.ExpiredSignatureError:
        await websocket.close(code=1008, reason="Token has expired")
        return None
    except jwt.exceptions.PyJWTError:
        await websocket.close(code=1008, reason="Could not validate credentials")
        return None

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from adapters.postgres.engine import get_session
from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.schemas.user_schema import UserSchema
from application.services.user_service import UserService

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyUnitOfWork:
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

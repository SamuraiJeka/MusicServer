import datetime
import jwt
import bcrypt

from config.settings import settings
from domain.ports.uow_interface import UoWInterface
from application.schemas.user_schema import PostUserSchema, UserSchema
from application.schemas.auth_schema import LoginSchema, TokenSchema
from application.mappers.user_mapper import UserMapper


class AuthService:
    def __init__(self, uow: UoWInterface):
        self._uow = uow

    async def registration(self, user_dto: PostUserSchema) -> UserSchema:
        async with self._uow:
            user_dto.password = await self.generate_hash_password(user_dto.password)
            user = await UserMapper.dto_to_entity(user_dto)
            user = await self._uow.user_repo.create(user)
            return await UserMapper.entity_to_dto(user)

    async def login(self, user_dto: LoginSchema) -> TokenSchema:
        async with self._uow:
            user = await self._uow.user_repo.get_by_email(user_dto.email)
            if not user:
                raise Exception
            if not await self.check_password(user_dto.password, user.hash_password):
                raise Exception
            return await self.generate_tokens(user_dto.email)

    async def refresh(self, refresh_token: str) -> TokenSchema:
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload["type"] != "refresh":
                raise Exception
            if datetime.datetime.fromtimestamp(payload["exp"]) < datetime.datetime.now():
                raise Exception

            email = payload["email"]
            tokens = await self.generate_tokens(email)
            return tokens
        except jwt.PyJWTError:
            raise Exception

    @staticmethod
    async def check_password( input_password: str, user_password: str) -> bool:
        return bcrypt.checkpw(input_password.encode(), user_password.encode())

    @staticmethod
    async def generate_hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    async def generate_tokens(email: str) -> TokenSchema:
        access_token_expires = datetime.timedelta(minutes=settings.ACCESS_EXPIRES_MIN)
        refresh_token_expires = datetime.timedelta(days=settings.REFRESH_EXPIRES_DAY)

        access_token_payload = {
            "email": email,
            "exp": datetime.datetime.now() + access_token_expires,
            "iat": datetime.datetime.now(),
            "type": "access"
        }
        access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, settings.ALGORITHM)

        refresh_token_payload = {
            "email": email,
            "exp": datetime.datetime.now() + refresh_token_expires,
            "iat": datetime.datetime.now(),
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, settings.ALGORITHM)

        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )

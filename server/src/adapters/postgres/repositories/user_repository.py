from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.entities.user import User
from domain.ports.repositories.user_repository_interface import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_by_id(self, user_id):
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email) 
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username):
        return await super().get_by_username(username)

    async def delete_by_id(self, user_id):
        return await super().delete_by_id(user_id)

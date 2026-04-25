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

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        await self._session.delete(user)
        await self._session.flush()
        return True

    async def search(self, query: str, limit: int, offset: int = 0) -> list[User]:
        q = query.strip()
        stmt = (
            select(User)
            .where(
                (User.username.ilike(f"%{q}%"))  # type: ignore[attr-defined]
                | (User.email.ilike(f"%{q}%"))  # type: ignore[attr-defined]
            )
            .order_by(User.id.desc())  # type: ignore[union-attr]
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

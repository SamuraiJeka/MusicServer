from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.repositories.user_repository_interface import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user):
        return await super().create(user)
    
    async def get_by_id(self, user_id):
        return await super().get_by_id(user_id)

    async def get_by_email(self, email):
        return await super().get_by_email(email)
    
    async def get_by_username(self, username):
        return await super().get_by_username(username)
    
    async def delete_by_id(self, user_id):
        return await super().delete_by_id(user_id)

from domain.ports.uow_interface import UoWInterface
from application.mappers.user_mapper import UserMapper
from application.schemas.user_schema import UserSchema


class UserService:
    def __init__(self, uow: UoWInterface):
        self._uow = uow

    async def get_by_email(self, email: str) -> UserSchema:
        user = await self._uow.user_repo.get_by_email(email)
        if user is None:
            raise Exception
        return await UserMapper.entity_to_dto(user)

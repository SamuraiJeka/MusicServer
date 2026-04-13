from domain.entities.user import User
from application.schemas.user_schema import UserSchema, PostUserSchema


class UserMapper:
    @staticmethod
    async def dto_to_entity(dto: PostUserSchema) -> User:
        return User(
            email=dto.email,
            hash_password=dto.password,
            username=dto.username,
        )

    @staticmethod
    async def entity_to_dto(entity: User) -> UserSchema:
        return UserSchema(
            id=entity.id,
            username=entity.username,
            email=entity.email,
        )

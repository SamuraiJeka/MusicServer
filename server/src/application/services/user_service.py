from domain.ports.uow_interface import UoWInterface
from application.mappers.user_mapper import UserMapper
from application.schemas.user_schema import UserSchema, UserMeSchema
from application.exceptions import BadRequestError, NotFoundError
from application.services.user_avatar_presign import presign_user_avatar

_AVATAR_MAX_BYTES = 5 * 1024 * 1024
_ALLOWED_EXT = frozenset({"jpg", "jpeg", "png", "webp", "gif"})


class UserService:
    def __init__(self, uow: UoWInterface):
        self._uow = uow

    async def get_by_email(self, email: str) -> UserSchema:
        user = await self._uow.user_repo.get_by_email(email)
        if user is None:
            raise Exception
        return await UserMapper.entity_to_dto(user)

    def _require_user_id(self, user: UserSchema) -> int:
        if user.id is None:
            raise BadRequestError("Authenticated user must have id")
        return user.id

    async def _me_schema(self, u) -> UserMeSchema:
        avatar_url = None
        key = getattr(u, "avatar_key", None)
        if key:
            avatar_url = await presign_user_avatar(key)
        uid = u.id
        if uid is None:
            raise NotFoundError("User not found")
        return UserMeSchema(
            id=uid,
            username=u.username,
            email=u.email,
            avatar_url=avatar_url,
        )

    async def get_me(self, user: UserSchema) -> UserMeSchema:
        async with self._uow:
            uid = self._require_user_id(user)
            u = await self._uow.user_repo.get_by_id(uid)
            if u is None:
                raise NotFoundError("User not found")
            return await self._me_schema(u)

    async def update_avatar(
        self,
        user: UserSchema,
        content: bytes,
        filename: str | None,
    ) -> UserMeSchema:
        if not content:
            raise BadRequestError("Empty file")
        if len(content) > _AVATAR_MAX_BYTES:
            raise BadRequestError("Image too large (max 5 MB)")
        ext = self._avatar_extension(filename)
        fname = f"profile{ext}"
        async with self._uow:
            uid = self._require_user_id(user)
            u = await self._uow.user_repo.get_by_id(uid)
            if u is None:
                raise NotFoundError("User not found")
            prefix = f"avatars/{uid}"
            old_key = getattr(u, "avatar_key", None)
            if old_key:
                p, fn = old_key.rsplit("/", 1)
                await self._uow.image_storage.delete(p, fn)
            await self._uow.image_storage.save(prefix, fname, content)
            u.avatar_key = f"{prefix}/{fname}"
            return await self._me_schema(u)
    
    @staticmethod
    def _avatar_extension(filename: str | None) -> str:
        if not filename or "." not in filename:
            return ".jpg"
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in _ALLOWED_EXT:
            raise BadRequestError("Allowed formats: jpg, jpeg, png, webp, gif")
        if ext == "jpeg":
            return ".jpg"
        return f".{ext}"

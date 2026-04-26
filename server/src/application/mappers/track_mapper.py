from datetime import timedelta

from application.schemas.music_schemas import TrackSchema
from domain.entities.track import Track
from application.exceptions import BadRequestError


class TrackMapper:
    @staticmethod
    async def dto_to_entity(
        owner_id: int,
        title: str,
        duration: timedelta,
        content: bytes,
        audio_key: str | None = None,
        view: int = 0,
        created_album_id: int | None = None,
    ) -> Track:
        return Track(
            id=None,
            owner_id=owner_id,
            title=title,
            audio_key=audio_key,
            view=view,
            duration=duration,
            content=content,
            created_album_id=created_album_id,
        )

    @staticmethod
    async def entity_to_dto(entity: Track) -> TrackSchema:
        if entity.id is None:
            raise BadRequestError("Track must be persisted before mapping to DTO")
        return TrackSchema(
            id=entity.id,
            owner_id=entity.owner_id,
            title=entity.title,
            audio_key=getattr(entity, "audio_key", None),
            created_album_id=getattr(entity, "created_album_id", None),
            duration=entity.duration,
            view=entity.view,
        )

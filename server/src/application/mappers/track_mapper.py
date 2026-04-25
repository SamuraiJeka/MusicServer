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
    ) -> Track:
        return Track(
            id=None,
            owner_id=owner_id,
            title=title,
            audio_key=audio_key,
            view=view,
            duration=duration,
            content=content,
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
            duration=entity.duration,
            view=entity.view,
        )

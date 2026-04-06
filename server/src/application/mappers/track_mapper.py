from datetime import timedelta

from application.schemas.music_schemas import TrackSchema
from domain.entities.track import Track


class TrackMapper:
    @staticmethod
    async def dto_to_entity(
        owner_id: int,
        title: str,
        duration: timedelta,
        content: bytes,
        view: int = 0,
    ) -> Track:
        return Track(
            id=None,
            owner_id=owner_id,
            title=title,
            view=view,
            duration=duration,
            content=content,
        )

    @staticmethod
    async def entity_to_dto(entity: Track) -> TrackSchema:
        if entity.id is None:
            raise ValueError("Track must be persisted before mapping to DTO")
        return TrackSchema(
            id=entity.id,
            owner_id=entity.owner_id,
            title=entity.title,
            duration=entity.duration,
            view=entity.view,
        )

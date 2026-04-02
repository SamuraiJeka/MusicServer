from datetime import timedelta

from src.domain.entities.track import Track
from src.application.mappers.track_mapper import TrackMapper


async def test_track_mapper_create_entity_and_entity_to_dto() -> None:
    duration = timedelta(seconds=180)
    content = b"audio-bytes"

    track: Track = await TrackMapper.dto_to_entity(
        owner_id=1,
        title="test-track",
        duration=duration,
        content=content,
    )

    assert track.id is None
    assert track.owner_id == 1
    assert track.title == "test-track"
    assert track.view == 0
    assert track.duration == duration
    assert track.content == content

    dto = await TrackMapper.entity_to_dto(track)

    assert dto.id is None
    assert dto.owner_id == 1
    assert dto.title == "test-track"
    assert dto.duration == duration
    assert dto.view == 0

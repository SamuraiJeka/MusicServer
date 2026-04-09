from datetime import timedelta

from src.domain.entities.user import User
from src.domain.entities.track import Track
from src.domain.entities.track_list import TrackList
from src.domain.entities.track_list import TrackListType

def _make_track(owner_id: int, title: str) -> Track:
    return Track(
        id=None,
        owner_id=owner_id,
        title=title,
        view=0,
        duration=timedelta(seconds=300),
        content=b"audio-bytes",
    )


def test_add_track_in_track_list() -> None:
    user = User("email@.com", hash_password="123", username="user")

    track1 = _make_track(owner_id=user.id, title="track1")
    track2 = _make_track(owner_id=user.id, title="track2")

    track_list = TrackList(
        id=None,
        owner_id=user.id,
        title="album",
        _type=TrackListType.ALBUM,
    )

    track_list.add_track(track1)
    assert len(track_list.track_list) == 1

    track_list.add_track(track2)
    assert len(track_list.track_list) == 2


def test_remove_track_in_track_list() -> None:
    user = User("email@.com", hash_password="123", username="user")

    track1 = _make_track(owner_id=user.id, title="track1")
    track2 = _make_track(owner_id=user.id, title="track2")

    track_list = TrackList(
        id=None,
        owner_id=user.id,
        title="album",
        _type=TrackListType.ALBUM,
    )

    track_list.add_track(track1)
    track_list.add_track(track2)

    track_list.remove_track(track1)

    assert len(track_list.track_list) == 1
    assert track_list.track_list[0] == track2


def test_duration_of_track_list() -> None:
    user = User("email@.com", hash_password="123", username="user")

    track1 = _make_track(owner_id=user.id, title="track1")
    track2 = _make_track(owner_id=user.id, title="track2")

    track_list = TrackList(
        id=None,
        owner_id=user.id,
        title="album",
        _type=TrackListType.ALBUM,
    )

    track_list.add_track(track1)
    assert track_list.duration == timedelta(seconds=300)

    track_list.add_track(track2)
    assert track_list.duration == timedelta(seconds=600)


def test_track_list_type_album_and_playlist() -> None:
    user = User("email@.com", hash_password="123", username="user")

    album = TrackList(
        id=None,
        owner_id=user.id,
        title="my-album",
        _type=TrackListType.ALBUM,
    )
    playlist = TrackList(
        id=None,
        owner_id=user.id,
        title="my-playlist",
        _type=TrackListType.PLAYLIST,
    )

    assert album._type == TrackListType.ALBUM
    assert playlist._type == TrackListType.PLAYLIST

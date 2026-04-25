from datetime import timedelta
from enum import Enum

from domain.entities.track import Track


class TrackListType(str, Enum):
    ALBUM = "album"
    PLAYLIST = "playlist"


class TrackList:
    def __init__(
        self,
        id: int | None,
        owner_id: int,
        title: str,
        _type: TrackListType,
        image_filename: str | None = None,
        ):
        self.id = id
        self.owner_id = owner_id
        self.title = title
        self._type = _type
        self.image_filename = image_filename
        self.track_list: list[Track] = []

    def __repr__(self):
        return f"<TrackList {self._type} {self.title}>"

    def add_track(self, track: Track) -> None:
        self.track_list.append(track)

    def remove_track(self, track: Track) -> None:
        self.track_list.remove(track)

    @property
    def duration(self) -> timedelta:
        return sum((track.duration for track in self.track_list), timedelta())

from datetime import timedelta

from src.domain.entities.user import User
from src.domain.entities.track import Track


class TrackList:
    def __init__(self, owner: User, title: str):
        self.owner = owner
        self.title = title
        self.track_list = []

    def __repr__(self):
        return f"<TrackList {self.title}>"

    def __eq__(self, other):
        if not isinstance(other, TrackList):
            return False
        return other.track_list == self.track_list

    def __hash__(self):
        return hash((self.owner.email, self.title))

    def add_track(self, track: Track) -> None:
        self.track_list.append(track)

    def remove_track(self, track: Track) -> None:
        self.track_list.remove(track)

    @property
    def duration(self) -> timedelta:
        return sum((track.duration for track in self.track_list), timedelta())

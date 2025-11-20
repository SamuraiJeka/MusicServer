from datetime import timedelta

from domain.track_model import Track


class TrackList:
    def __init__(self, user_id: int, title: str, track_list: list[Track] = []):
        self.user_id = user_id
        self.title = title
        self.track_list = track_list

    def __repr__(self):
        return f"<TrackList {self.title}>"

    def __eq__(self, other):
        if not isinstance(other, TrackList):
            return False
        return other.track_list == self.track_list

    def __hash__(self):
        return hash((self.user_id, self.title))

    async def add_track(self, track: Track) -> None:
        self.track_list.append(track)

    async def remove_track(self, track: Track) -> None:
        self.track_list.remove(track)

    @property
    def duration(self) -> timedelta:
        return sum((track.duration for track in self.track_list), timedelta())

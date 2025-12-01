from src.domain.entities.user import User
from src.domain.entities.track import Track
from src.domain.entities.track_list import TrackList

from datetime import timedelta


def test_add_track_in_track_list():
    user = User("email@.com", hash_password="123", username="user")
    track1 = Track(user, title="track1", path_dir="photo_path1", view=0, duration=timedelta(seconds=300))
    track2 = Track(user, title="track2", path_dir="photo_path2", view=0, duration=timedelta(seconds=300))
    track_list = TrackList(user, title="album")

    track_list.add_track(track=track1)
    assert len(track_list.track_list) == 1

    track_list.add_track(track=track2)
    assert len(track_list.track_list) == 2


def test_remove_track_in_track_list():
    user = User("email@.com", hash_password="123", username="user")
    track1 = Track(user, title="track1", path_dir="photo_path1", view=0, duration=timedelta(seconds=300))
    track2 = Track(user, title="track2", path_dir="photo_path2", view=0, duration=timedelta(seconds=300))
    track_list = TrackList(user, title="album")

    track_list.add_track(track=track1)
    track_list.add_track(track=track2)

    track_list.remove_track(track=track1)

    assert len(track_list.track_list) == 1


def test_duration_of_track_list():
    user = User("email@.com", hash_password="123", username="user")
    track1 = Track(user, title="track1", path_dir="photo_path1", view=0, duration=timedelta(seconds=300))
    track2 = Track(user, title="track2", path_dir="photo_path2", view=0, duration=timedelta(seconds=300))
    track_list = TrackList(user, title="album")

    track_list.add_track(track=track1)
    assert track_list.duration == timedelta(seconds=300)

    track_list.add_track(track=track2)
    assert track_list.duration == timedelta(seconds=600)

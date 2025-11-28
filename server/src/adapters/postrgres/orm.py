from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    BigInteger,
    Interval,
    ForeignKey,
)
from sqlalchemy.orm import mapper, relationship

from domain.entities.user import User
from domain.entities.track import Track
from domain.entities.track_list import TrackList

metadata = MetaData()


users = Table(
    "users",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("email", String(255), unique=True, nullable=False),
    Column("username", String(32), nullable=False),
    Column("hash_password", String(255), nullable=False),
)


tracks = Table(
    "tracks",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("path_dir", String(512), unique=True, nullable=False),
    Column("view", BigInteger, nullable=False, server_default="0"),
    Column("duration", Interval, nullable=False),
    Column("owner_id", ForeignKey("users.id"), nullable=False),
)


track_lists = Table(
    "track_lists",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("owner_id", ForeignKey("users.id"), nullable=False),
)


tracks_track_lists = Table(
    "tracks_track_lists",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("track_id", ForeignKey("tracks.id")),
    Column("track_list_id", ForeignKey("track_lists.id")),
)


def start_mappers():
    mapper(
        User,
        users,
        properties={
            "tracks": relationship(Track, back_populates="owner"),
            "track_lists": relationship(TrackList, back_populates="owner"),
        },
    )
    mapper(
        Track,
        tracks,
        properties={
            "owner": relationship(User, back_populates="tracks"),
            "lists": relationship(
                TrackList,
                secondary=tracks_track_lists,
                back_populates="track_list",
            ),
        },
    )
    mapper(
        TrackList,
        track_lists,
        properties={
            "owner": relationship(User, back_populates="track_lists"),
            "track_list": relationship(
                Track,
                secondary=tracks_track_lists,
                back_populates="lists",
            ),
        },
    )

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    BigInteger,
    Interval,
    ForeignKey,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import registry, relationship, clear_mappers

from domain.entities.user import User
from domain.entities.track import Track
from domain.entities.track_list import TrackList, TrackListType

metadata = MetaData()
mapper_registry = registry()


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
    Column("_type", SAEnum(TrackListType, name="track_list_type"), nullable=False),
)


tracks_track_lists = Table(
    "tracks_track_lists",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("track_id", ForeignKey("tracks.id")),
    Column("track_list_id", ForeignKey("track_lists.id")),
    Column("position", BigInteger, nullable=True),
)

def start_mappers():
    clear_mappers()

    mapper_registry.map_imperatively(
        User,
        users,
        properties={
            "tracks": relationship(Track, back_populates="owner"),
            "track_lists": relationship(TrackList, back_populates="owner"),
        },
    )

    mapper_registry.map_imperatively(
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

    mapper_registry.map_imperatively(
        TrackList,
        track_lists,
        properties={
            "owner": relationship(User, back_populates="track_lists"),
            "track_list": relationship(
                Track,
                secondary=tracks_track_lists,
                back_populates="lists",
                order_by=(
                    tracks_track_lists.c.position.asc().nulls_last(),
                    tracks_track_lists.c.id.asc(),
                ),
            ),
        },
    )

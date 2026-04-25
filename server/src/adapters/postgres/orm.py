from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    BigInteger,
    Interval,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import registry, relationship, clear_mappers

from domain.entities.user import User
from domain.entities.track import Track
from domain.entities.track_list import TrackList, TrackListType
from domain.entities.chat import Chat
from domain.entities.chat_member import ChatMember
from domain.entities.message import Message, MessageType

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
    Column("audio_key", String(512), nullable=True),
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
    Column("image_filename", String(255), nullable=True),
)


tracks_track_lists = Table(
    "tracks_track_lists",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("track_id", ForeignKey("tracks.id")),
    Column("track_list_id", ForeignKey("track_lists.id")),
    Column("position", BigInteger, nullable=True),
)


chats = Table(
    "chats",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


chat_members = Table(
    "chat_members",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE"), nullable=False),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Index("ix_chat_members_chat_id", "chat_id"),
    Index("ix_chat_members_user_id", "user_id"),
    Index("ux_chat_members_chat_user", "chat_id", "user_id", unique=True),
)


messages = Table(
    "messages",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE"), nullable=False),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("type", SAEnum(MessageType, name="message_type"), nullable=False),
    Column("text", Text, nullable=True),
    Column("audio_key", String(512), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index("ix_messages_chat_id", "chat_id"),
    Index("ix_messages_created_at", "created_at"),
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

    mapper_registry.map_imperatively(
        Chat,
        chats,
    )

    mapper_registry.map_imperatively(
        ChatMember,
        chat_members,
    )

    mapper_registry.map_imperatively(
        Message,
        messages,
        properties={
            "chat": relationship(Chat),
            "user": relationship(User),
        },
    )

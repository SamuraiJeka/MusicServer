"""tracks created_album_id

Revision ID: 4b7f7e2c9d12
Revises: a03080f20025
Create Date: 2026-04-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b7f7e2c9d12"
down_revision: Union[str, Sequence[str], None] = "a03080f20025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tracks", sa.Column("created_album_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_tracks_created_album_id_track_lists",
        "tracks",
        "track_lists",
        ["created_album_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tracks_created_album_id_track_lists", "tracks", type_="foreignkey")
    op.drop_column("tracks", "created_album_id")


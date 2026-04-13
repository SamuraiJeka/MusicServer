"""add track order position

Revision ID: 3f0d7c7e1c4b
Revises: d81e4329f422
Create Date: 2026-04-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3f0d7c7e1c4b"
down_revision: Union[str, Sequence[str], None] = "d81e4329f422"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tracks_track_lists", sa.Column("position", sa.BigInteger(), nullable=True))
    op.create_index(
        "ix_tracks_track_lists_track_list_id_position",
        "tracks_track_lists",
        ["track_list_id", "position"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tracks_track_lists_track_list_id_position", table_name="tracks_track_lists")
    op.drop_column("tracks_track_lists", "position")


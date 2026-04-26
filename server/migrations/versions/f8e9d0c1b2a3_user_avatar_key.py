"""user avatar_key

Revision ID: f8e9d0c1b2a3
Revises: e3b72ab1144a
Create Date: 2026-04-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f8e9d0c1b2a3"
down_revision: Union[str, Sequence[str], None] = "e3b72ab1144a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_key", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_key")

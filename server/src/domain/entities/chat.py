from __future__ import annotations

from datetime import datetime


class Chat:
    def __init__(
        self,
        id: int | None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.created_at = created_at

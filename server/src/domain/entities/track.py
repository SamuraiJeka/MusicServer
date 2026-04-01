from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=False)
class Track:
    id: int | None
    owner_id: int
    title: str
    view: int
    duration: timedelta
    content: bytes

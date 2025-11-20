from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=False)
class Track:
    creator_id: int
    path_dir: str
    view: int
    duration: timedelta

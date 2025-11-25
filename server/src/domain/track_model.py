from dataclasses import dataclass
from datetime import timedelta

from domain.user_model import User


@dataclass(frozen=False)
class Track:
    owner: User
    title: str
    path_dir: str
    view: int
    duration: timedelta

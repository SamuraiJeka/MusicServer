from dataclasses import dataclass


@dataclass(frozen=False)
class User:
    email: str
    hash_password: str
    username: str
    id: int | None = None
    avatar_key: str | None = None

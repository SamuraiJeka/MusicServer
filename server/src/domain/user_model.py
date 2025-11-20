from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    email: str
    hash_password: str
    username: str

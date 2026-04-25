from __future__ import annotations


class ChatMember:
    def __init__(
        self,
        id: int | None,
        chat_id: int,
        user_id: int,
    ) -> None:
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id

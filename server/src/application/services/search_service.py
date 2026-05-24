from application.exceptions import BadRequestError
from application.schemas.search_schemas import ArtistSchema, GlobalSearchResponseSchema, MessengerUserSchema
from application.schemas.user_schema import UserSchema
from application.mappers.track_list_mapper import TrackListMapper
from application.mappers.track_mapper import TrackMapper
from application.services.chat_service import _message_preview
from domain.entities.user import User
from domain.ports.uow_interface import UoWInterface


class SearchService:
    def __init__(self, uow: UoWInterface) -> None:
        self._uow = uow

    async def global_search(self, query: str, limit: int, offset: int = 0) -> GlobalSearchResponseSchema:
        async with self._uow:
            users = await self._uow.user_repo.search(query=query, limit=limit, offset=offset)
            albums = await self._uow.track_list_repo.search_albums(query=query, limit=limit, offset=offset)
            tracks = await self._uow.track_repo.search_by_title(query=query, limit=limit, offset=offset)

            return GlobalSearchResponseSchema(
                artists=[ArtistSchema(id=u.id, username=u.username) for u in users if u.id is not None],
                albums=[TrackListMapper.album_entity_to_summary(a) for a in albums],
                tracks=[await TrackMapper.entity_to_dto(t) for t in tracks],
            )

    async def _enrich_messenger_user(
        self,
        user_id: int,
        peer: User,
        partner_set: set[int],
    ) -> MessengerUserSchema | None:
        if peer.id is None:
            return None
        has_chat = peer.id in partner_set
        chat_id = None
        last_message = None
        if has_chat:
            chat = await self._uow.chat_repo.get_private_chat(user_id, peer.id)
            if chat and chat.id:
                chat_id = chat.id
                last_by_chat = await self._uow.message_repo.get_last_by_chats([chat.id])
                last = last_by_chat.get(chat.id)
                if last:
                    last_message = _message_preview(last)
        return MessengerUserSchema(
            id=peer.id,
            username=peer.username,
            has_chat=has_chat,
            chat_id=chat_id,
            last_message=last_message,
        )

    async def messenger_user_search(
        self,
        user: UserSchema,
        query: str,
        limit: int,
        offset: int = 0,
    ) -> list[MessengerUserSchema]:
        if user.id is None:
            raise BadRequestError("Authenticated user must have id")
        user_id = user.id
        q = query.strip()

        async with self._uow:
            partner_ids = await self._uow.chat_repo.list_private_chat_partner_ids(user_id)
            partner_set = set(partner_ids)

            if not q:
                if not partner_ids:
                    return []

                peers = await self._uow.user_repo.get_by_ids(partner_ids)
                peer_by_id = {p.id: p for p in peers if p.id is not None}

                rows: list[tuple[MessengerUserSchema, object]] = []
                for pid in partner_ids:
                    peer = peer_by_id.get(pid)
                    if peer is None:
                        continue
                    chat = await self._uow.chat_repo.get_private_chat(user_id, pid)
                    if chat is None or chat.id is None:
                        continue
                    last_by_chat = await self._uow.message_repo.get_last_by_chats([chat.id])
                    last = last_by_chat.get(chat.id)
                    sort_at = last.created_at if last and last.created_at else chat.created_at
                    rows.append(
                        (
                            MessengerUserSchema(
                                id=peer.id,
                                username=peer.username,
                                has_chat=True,
                                chat_id=chat.id,
                                last_message=_message_preview(last) if last else None,
                            ),
                            sort_at,
                        )
                    )
                rows.sort(key=lambda r: r[1], reverse=True)
                return [r[0] for r in rows[offset : offset + limit]]

            # Сначала собеседники с диалогом, затем остальные — поиск только по нику
            q_lower = q.lower()
            peers = await self._uow.user_repo.get_by_ids(partner_ids)
            partner_matches = [
                p for p in peers if p.id is not None and q_lower in p.username.lower()
            ]
            partner_matches.sort(key=lambda u: u.username.lower())

            remaining = limit + offset - len(partner_matches)
            other_matches: list[User] = []
            if remaining > 0:
                other_matches = await self._uow.user_repo.search_by_username(
                    query=q,
                    limit=remaining,
                    offset=0,
                    exclude_ids=[user_id, *partner_ids],
                )

            combined = partner_matches + other_matches
            page = combined[offset : offset + limit]

            out: list[MessengerUserSchema] = []
            for u in page:
                dto = await self._enrich_messenger_user(user_id, u, partner_set)
                if dto:
                    out.append(dto)
            return out

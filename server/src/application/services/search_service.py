from application.schemas.search_schemas import ArtistSchema, GlobalSearchResponseSchema
from application.mappers.track_list_mapper import TrackListMapper
from application.mappers.track_mapper import TrackMapper
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

    async def messenger_user_search(self, query: str, limit: int, offset: int = 0) -> list[ArtistSchema]:
        async with self._uow:
            users = await self._uow.user_repo.search(query=query, limit=limit, offset=offset)
            return [ArtistSchema(id=u.id, username=u.username) for u in users if u.id is not None]

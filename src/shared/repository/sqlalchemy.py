from typing import Any, AsyncContextManager, Callable, List, Optional, Self, Tuple, Type, TypeVar, Union, cast

from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, select

from shared.exceptions import NotFoundError
from shared.repository.ports.generic import AbstractRepository, FilterBy


EntityT = TypeVar('EntityT')
CreateT = TypeVar('CreateT', bound=BaseModel)
UpdateT = TypeVar('UpdateT', bound=BaseModel)


class SqlAlchemyRepository(AbstractRepository[EntityT, CreateT, UpdateT]):
    entity: Type[EntityT]
    default_key_param = 'uuid'

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ARG003
        base: Optional[Tuple[Any, ...]] = getattr(cls, '__orig_bases__', None)
        if base:
            generics: Tuple[Type[EntityT], Type[CreateT], Type[UpdateT]] = base[0].__args__
            cls.entity = generics[0]
        return super().__new__(cls)

    def __init__(
        self,
        session: Callable[[], AsyncContextManager[AsyncSession]],
    ) -> None:
        self.session_factory = session

    def get_key_param(
        self,
    ) -> str:
        return getattr(self, 'key', self.default_key_param)

    async def get_by_id(self, uuid: Union[str, int]) -> EntityT:
        by = {self.get_key_param(): uuid}
        try:
            async with self.session_factory() as session:
                query = select(self.entity).filter_by(**by)
                results = await session.execute(query)
                (result,) = results.one()
        except NoResultFound:
            raise NotFoundError(self.entity.__name__)
        else:
            return cast(EntityT, result)

    # From: https://github.com/lewoudar/fastapi-paginator/blob/main/fastapi_paginator/helpers.py
    async def _paginate(self, query: Select, page: int, size: int) -> List[EntityT]:
        # inspiration for this query comes from fastapi-pagination package
        async with self.session_factory() as session:
            return list(await session.scalars(query.limit(size).offset(page - 1)))

    async def get_all(self) -> List[EntityT]:
        query = select(self.entity)
        async with self.session_factory() as session:
            return list((await session.scalars(query)).all())

    async def get_xpage(self, page: int, size: int) -> List[EntityT]:
        query = select(self.entity)
        return await self._paginate(query, page, size)

    async def filter_by(self, by: FilterBy) -> List[EntityT]:
        query = select(self.entity).filter_by(**by)
        async with self.session_factory() as session:
            return list((await session.scalars(query)).all())

    async def create(self, data: CreateT) -> EntityT:
        async with self.session_factory() as session:
            instance = self.entity(**data.model_dump())
            session.add(instance)
        return instance

    async def update(self, uuid: Union[str, int], data: UpdateT) -> EntityT:
        to_update = data.model_dump(exclude_unset=True)
        if not to_update:
            raise ValueError('No data to update')
        async with self.session_factory() as session:
            instance = await self.get_by_id(uuid)

            for key, value in to_update.items():
                setattr(instance, key, value)

            session.add(instance)
        return instance

    async def delete(self, uuid: Union[str, int]) -> None:
        async with self.session_factory() as session:
            instance = await self.get_by_id(uuid)
            await session.delete(instance)

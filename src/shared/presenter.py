import abc
from typing import Generic, TypeVar


InT = TypeVar('InT')
OutT = TypeVar('OutT')


class AbstractPresenter(Generic[InT, OutT], abc.ABC):
    result: OutT

    @abc.abstractmethod
    async def present(self, data: InT) -> None:
        ...

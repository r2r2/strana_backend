from abc import ABC, abstractmethod
from typing import Optional, Type, NamedTuple


class AbstractCORHandler(ABC):
    """Интерфейс хэндера в цепочке зависимостей"""
    state: Optional[NamedTuple]

    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def handle(self, *args, **kwargs) -> 'AbstractCORHandler.state':
        raise NotImplementedError

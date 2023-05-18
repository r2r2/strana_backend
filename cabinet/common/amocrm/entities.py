import abc

from common.orm.entities import BaseRepo


class BaseAmocrmRepo(BaseRepo):
    """
    Basic repository for amocrm models
    """


class BaseAmocrmService(abc.ABC):
    """
    Base class for amocrm services
    """
    async def __call__(self, *args, **kwargs):
        raise NotImplementedError

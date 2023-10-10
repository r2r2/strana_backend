# pylint: disable=broad-except,redefined-builtin
from asyncio import Future, ensure_future, gather
from copy import copy
from typing import Any, Callable, Type

from config import tortoise_config
from src.properties import repos as properties_repos
from src.properties.services import ImportPropertyServiceFactory
from tortoise import Model, Tortoise


class UpdatePropertiesManage:
    """
    Обновление всех квартир с портала
    """
    def __init__(self) -> None:
        import_property_service = ImportPropertyServiceFactory.create()
        self.service: Callable = import_property_service
        self.property_repo: properties_repos.PropertyRepo = properties_repos.PropertyRepo()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

    async def __call__(self, *args, **kwargs) -> None:
        await self.orm_class.init(config=self.orm_config)
        futures: list[Future] = []
        properties: list[Model] = await self.property_repo.list()
        for _property in properties:
            futures.append(ensure_future(self.import_property(property_id=_property.id)))
        await gather(*futures)
        await self.orm_class.close_connections()

    async def import_property(self, property_id: int) -> None:
        try:
            await self.service(property_id=property_id)
        except Exception:
            pass

# pylint: disable=broad-except,redefined-builtin
import structlog
import binascii
from copy import copy
from typing import Any, Type
from pydantic import ValidationError

from config import tortoise_config
from src.properties import repos as properties_repos
from src.users import repos as users_repos
from tortoise import Tortoise

from common.utils import from_global_id


class UpdateInterestPropertiesManage:
    """
    Добавление ко всем объектам в избранном profitbase_id.
    """

    def __init__(self) -> None:
        self.global_id_decoder = from_global_id
        self.property_repo: properties_repos.PropertyRepo = properties_repos.PropertyRepo()
        self.interests_repo: users_repos.InterestsRepo = users_repos.InterestsRepo()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

        self.logger: structlog.BoundLogger = structlog.get_logger(__name__)

    async def __call__(self, *args, **kwargs) -> None:
        await self.orm_class.init(config=self.orm_config)

        interests_property_global_ids: list[str] = await self.interests_repo.list().distinct().values_list(
            "property__global_id",
            flat=True,
        )

        filters = dict(
            global_id__in=interests_property_global_ids,
            profitbase_id__isnull=True,
        )
        interested_properties: list[properties_repos.Property] = await self.property_repo.list(filters=filters)
        self.logger.info(
            f"Объекты недвижимости в избранном без profitbase_id, в количестве - "
            f"{len(interested_properties)} шт.\n"
            f"Список id объектов - {[interested_property.id for interested_property in interested_properties]}\n"
        )

        updated_interested_properties = []
        for interest_property in interested_properties:
            if profitbase_id := self._get_profitbase_id(interest_property.global_id):
                updated_interested_property: properties_repos.Property = await self.property_repo.update(
                    model=interest_property,
                    data=dict(profitbase_id=profitbase_id),
                )
                updated_interested_properties.append(updated_interested_property)
        self.logger.info(
            f"Обновленные объекты недвижимости в избранном с profitbase_id, в количестве - "
            f"{len(updated_interested_properties)} шт.\n"
            f"Список id объектов - "
            f"{[updated_interested_property.id for updated_interested_property in updated_interested_properties]}\n"
        )
        await self.orm_class.close_connections()

    def _get_profitbase_id(self, global_id: str) -> int | None:
        try:
            profitbase_id = int(from_global_id(global_id)[1])
        except (binascii.Error, UnicodeDecodeError, ValidationError, ValueError):
            profitbase_id = None
        return profitbase_id

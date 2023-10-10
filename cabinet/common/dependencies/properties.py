from typing import Optional, Type

from fastapi import Body
from src.properties.repos import PropertyRepo
from src.properties.services import ImportPropertyService, ImportPropertyServiceFactory


class PropertiesFromGlobalId:
    """Get property ids from global property ids"""
    def __init__(
            self,
            properties_repo: Type[PropertyRepo],
            import_property_service: Optional[ImportPropertyService] = None
    ):
        self.properties_repo = properties_repo()
        if not import_property_service:
            # should be loaded from di-container but now it`s creating an instance if dep is not provided
            import_property_service = ImportPropertyServiceFactory.create()
        self.import_property_service: ImportPropertyService = import_property_service

    async def __call__(
            self, property_global_ids: list[str] = Body(..., embed=True)
    ) -> list[int]:
        res_ids = []
        global_ids = set(property_global_ids)
        for global_id in global_ids:
            res_ids.append(await self._create_or_update_backend_property(global_id))
        return res_ids

    async def _create_or_update_backend_property(self, global_id) -> int:
        """
        Создаём или обновляем объект по данным из БД портала
        """
        data = dict(global_id=global_id)
        _property = await self.properties_repo.retrieve(filters=data)
        if not _property:
            _property = await self.properties_repo.create(data)

        await self.import_property_service(property=_property)
        return _property.id

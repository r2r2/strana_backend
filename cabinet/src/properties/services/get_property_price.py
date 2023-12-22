from typing import Type

import structlog

from src.properties.repos import Property
from src.payments.repos import PropertyPriceRepo, PropertyPrice, PropertyPriceTypeRepo, PropertyPriceType

from ..entities import BasePropertyService


class GetPropertyPriceService(BasePropertyService):
    """
    Сервис для получения экземпляра цены (модель 'PropertyPrice') объекта недвижимости.
    """

    def __init__(
        self,
        property_price_repo: Type[PropertyPriceRepo],
        property_price_type_repo: Type[PropertyPriceTypeRepo],
    ):
        self.property_price_repo: PropertyPriceRepo = property_price_repo()
        self.property_price_type_repo: PropertyPriceTypeRepo = property_price_type_repo()

        self.logger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, property: Property, property_price_type_slug: str) -> PropertyPrice | None:
        property_price_type: PropertyPriceType = await self.property_price_type_repo.retrieve(
            filters=dict(slug=property_price_type_slug),
            related_fields=["price_offer"],
        )
        if not property_price_type:
            self.logger.error(f"Не найден тип цены объектов недвижимости со слагом {property_price_type_slug=}")
            return

        if not property_price_type.price_offer:
            self.logger.error(f"У типа цены со слагом {property_price_type_slug=} не задана матрица предложения цены")
            return

        property_price: PropertyPrice = await self.property_price_repo.create(
            data=dict(
                property=property,
                price_type=property_price_type,
                price=property.original_price if property_price_type.price_offer.by_dev else property.final_price
            )
        )
        self.logger.info(f"Создан новый объект цены недвижимости {property_price=}")
        prefetch_fields: list[str] = [
            "price_type__price_offer",
            "price_type__price_offer__payment_method",
            "price_type__price_offer__price_type",
            "price_type__price_offer__mortgage_type",
        ]
        await property_price.fetch_related(*prefetch_fields)

        return property_price

from typing import Type

import structlog

from src.payments.repos import PropertyPriceRepo, PropertyPrice
from src.payments import repos as payment_repos

from ..entities import BasePropertyService


class GetPropertyPriceService(BasePropertyService):
    """
    Сервис для получения экземпляра цены (модель 'PropertyPrice') объекта недвижимости.
    """

    def __init__(
        self,
        property_price_repo: Type[PropertyPriceRepo],
        price_offer_matrix_repo: type[payment_repos.PriceOfferMatrixRepo],
    ):
        self.property_price_repo: PropertyPriceRepo = property_price_repo()
        self.price_offer_matrix_repo: payment_repos.PriceOfferMatrixRepo = price_offer_matrix_repo()

        self.logger = structlog.get_logger(self.__class__.__name__)

    async def __call__(
        self,
        property_id: int,
        property_payment_method_slug: str,
        property_mortgage_type_by_dev: bool | None,
    ) -> tuple[PropertyPrice | None, payment_repos.PriceOfferMatrix | None]:

        price_offer_matrix: payment_repos.PriceOfferMatrix | None = await self.price_offer_matrix_repo.retrieve(
            filters=dict(
                payment_method__slug=property_payment_method_slug,
                mortgage_type__by_dev=property_mortgage_type_by_dev,
            ),
            related_fields=["price_type"],
            ordering="priority",
        )
        if not price_offer_matrix or not price_offer_matrix.price_type:
            self.logger.error(
                f"Не не задана матрица предложения цены c параметрами "
                f"{property_payment_method_slug=}, {property_mortgage_type_by_dev=}"
            )

            price_offer_matrix: payment_repos.PriceOfferMatrix | None = await self.price_offer_matrix_repo.retrieve(
                filters=dict(default=True),
                ordering="priority",
            )
            self.logger.info(f"Найдена матрица предложения цены по умолчанию {price_offer_matrix=}")

            property_price: PropertyPrice = await self.property_price_repo.retrieve(
                filters=dict(
                    property_id=property_id,
                    price__isnull=False,
                    price_type__default=True,
                ),
            )
            self.logger.info(f"Найден объект цены недвижимости с типом по умолчанию {property_price=}")

        else:
            property_price: PropertyPrice = await self.property_price_repo.retrieve(
                filters=dict(
                    property_id=property_id,
                    price__isnull=False,
                    price_type_id=price_offer_matrix.price_type_id,
                ),
            )
            self.logger.info(f"Найден объект цены недвижимости (по умолчанию) {property_price=}")

        return property_price, price_offer_matrix

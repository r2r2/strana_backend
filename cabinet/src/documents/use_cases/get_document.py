from typing import Any, Type, Optional

from common.numbers import number_to_text
from ..entities import BaseDocumentCase
from ..exceptions import DocumentNotFoundError
from ..repos import Document, DocumentRepo
from ..types import DocumentSession


class GetDocumentCase(BaseDocumentCase):
    """
    Получение документа
    """

    price_units = (("рубль", "рубля", "рублей"), "m")
    period_units = (("календарный день", "календарных дня", "календарных дней"), "m")

    def __init__(
        self,
        session: DocumentSession,
        session_config: dict[str, Any],
        document_repo: Type[DocumentRepo],
    ) -> None:
        self.document_repo: DocumentRepo = document_repo()

        self.session: DocumentSession = session

        self.document_key: str = session_config["document_key"]

    async def __call__(self) -> Document:
        # document_info: dict[str, Any] = await self.session.get(self.document_key)
        # if (
        #     document_info
        #     and document_info["city"] is not None
        #     and document_info["address"] is not None
        #     and document_info["premise"] is not None
        #     and document_info["premise"] is not None
        #     and document_info["period"] is not None
        #
        # ):
        #     city: str = document_info["city"]
        #     address: str = document_info["address"]
        #     premise: str = document_info["premise"]
        #     price: int = document_info["price"]
        #     try:
        #         period: int = int(document_info["period"])
        #     except ValueError:
        #         raise DocumentNotFoundError
        # else:
        #     raise DocumentNotFoundError
        city = "reglament"
        filters: dict[str, Any] = dict(slug=city)
        document: Document = await self.document_repo.retrieve(filters=filters)
        if not document:
            raise DocumentNotFoundError

        document.text = document.text.format(
            address="address",
            premise="premise",
            price=5000,
            period=self._get_period_text(10),
        )
        return document

    @classmethod
    def _get_price_text(cls, price: int) -> str:
        price_as_text = number_to_text(price, cls.price_units).capitalize()
        price_unit = price_as_text.rsplit(" ", 1)[-1]

        # 5000.00 рублей (Пять тысяч рублей ноль копеек)
        return "{price}.00 {price_unit} ({price_as_text} ноль копеек)".format(
            price=price, price_unit=price_unit, price_as_text=price_as_text
        )

    @classmethod
    def _get_period_text(cls, period: int) -> str:
        period_as_text_with_units = number_to_text(period, cls.period_units).capitalize()
        period_as_text_without_units = number_to_text(period).capitalize()

        period_unit: Optional[str] = None
        for _period_unit in cls.period_units[0]:
            if _period_unit in period_as_text_with_units:
                period_unit = _period_unit
                break

        # 20 (Двадцать) календарных дней
        return "{period} ({period_as_text}) {period_unit}".format(
            period=period, period_as_text=period_as_text_without_units, period_unit=period_unit
        )

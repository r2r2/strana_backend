from datetime import datetime
from typing import Union

from common import cfields
from common.models import TimeBasedMixin
from src.agencies.repos import Agency
from src.booking.repos import Booking
from tortoise import Model, fields

from .agreement_status import AgreementStatus


class BaseAgreement(Model, TimeBasedMixin):
    id: int = fields.IntField(description="ID", pk=True, index=True)
    number: str = fields.CharField(description="Номер документа", max_length=50, null=True)
    status: fields.ForeignKeyRelation[AgreementStatus] = fields.ForeignKeyField(
        model_name="models.AgreementStatus", description="Статус", on_delete=fields.CASCADE, null=True,
    )
    agency: fields.ForeignKeyRelation[Agency] = fields.ForeignKeyField(
        model_name="models.Agency", description='Агентство', on_delete=fields.CASCADE
    )
    booking: fields.ForeignKeyRelation[Booking] = fields.ForeignKeyField(
        model_name="models.Booking", description='Бронь', on_delete=fields.CASCADE,
    )
    signed_at: datetime = fields.DatetimeField(description="Когда подписано", null=True)
    template_name: str = fields.CharField(description="Название шаблона", max_length=200)
    files: Union[list, dict] = cfields.MutableDocumentContainerField(description="Файлы", null=True)

    booking_id: int

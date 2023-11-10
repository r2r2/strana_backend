import uuid
from datetime import datetime

from tortoise import Model, fields
from common.orm.mixins import CRUDMixin
from ..entities import BaseOfferRepo


class Offer(Model):
    """
    Модель Коммерческого предложения
    """
    id: int
    booking_amo_id: int = fields.IntField(description="ID сделки в АМО")
    client_amo_id: int = fields.IntField(description="ID клиента в АМО")
    offer_link: str = fields.CharField(max_length=250, null=True, description="Ссылка на КП в Тильда")
    created_at: datetime = fields.DatetimeField(description="Дата и время создания", auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(description="Дата и время обновления", auto_now=True)
    uid: uuid = fields.UUIDField(description="ID КП в АМО", null=True)
    source: fields.ForeignKeyNullableRelation["OfferSource"] = fields.ForeignKeyField(
        model_name="models.OfferSource",
        on_delete=fields.SET_NULL,
        null=True,
        related_name="source_offers",
        description="Источник КП",
    )

    def __repr__(self):
        return f"{self.client_amo_id} - {self.booking_amo_id}"

    class Meta:
        table = "offers_offer"


class OfferRepo(BaseOfferRepo, CRUDMixin):
    """
    Репозиторий коммерческого предложения
    """

    model = Offer

from tortoise import Model, fields
from common.orm.mixins import CRUDMixin
from ..entities import BaseOfferPropertyRepo


class OfferProperty(Model):
    """
    Модель Объекты недвижимости для КП
    """
    id: int
    offer: fields.ForeignKeyRelation["Offer"] = fields.ForeignKeyField(
        model_name="models.Offer",
        on_delete=fields.CASCADE,
        related_name="offer_properties",
        description="Коммерческое предложение",
    )
    property_glogal_id: str = fields.CharField(max_length=250, description="Global ID объекта собственности")

    def __repr__(self):
        return f'{self.offer.client_amo_id} - {self.offer.booking_amo_id} - {self.property_glogal_id}'

    class Meta:
        table = "offers_offer_property"


class OfferPropertyRepo(BaseOfferPropertyRepo, CRUDMixin):
    """
    Репозиторий коммерческого предложения
    """

    model = OfferProperty

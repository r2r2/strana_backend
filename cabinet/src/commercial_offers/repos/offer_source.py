from tortoise import Model, fields
from common.orm.mixins import CRUDMixin
from ..entities import BaseOfferSourceRepo


class OfferSource(Model):
    """
    Модель Источнк коммерческого предложения
    """
    id: int
    name: str = fields.CharField(description="Название источника", max_length=150)
    slug: int = fields.CharField(description="Slug источника", max_length=32)

    def __repr__(self):
        return self.name

    class Meta:
        table = "offers_offer_source"


class OfferSourceRepo(BaseOfferSourceRepo, CRUDMixin):
    """
    Репозиторий коммерческого предложения
    """

    model = OfferSource

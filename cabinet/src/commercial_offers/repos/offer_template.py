from tortoise import Model, fields
from common.orm.mixins import CRUDMixin
from ..entities import BaseTemplateRepo


class OfferTemplate(Model):
    """
    Модель Шаблоны КП
    """
    id: int
    building: fields.ForeignKeyNullableRelation["Building"] = fields.ForeignKeyField(
        model_name="models.Building",
        on_delete=fields.CASCADE,
        related_name="offer_templates",
        description="Корпус",
    )
    name: str = fields.CharField(max_length=250, null=True, description="Название шаблона")
    is_default: bool = fields.BooleanField(description="Шаблон по умолчанию?", default=False)
    link: str = fields.CharField(max_length=512, null=True, description="Ссылка на шаблон в Тильда")
    site_id: int = fields.IntField(null=True, description="ID сайта")
    page_id: int = fields.IntField(null=True, description="ID страницы")

    def __repr__(self):
        return self.name

    class Meta:
        table = "offers_template"


class OfferTemplateRepo(BaseTemplateRepo, CRUDMixin):
    """
    Репозиторий коммерческого предложения
    """

    model = OfferTemplate

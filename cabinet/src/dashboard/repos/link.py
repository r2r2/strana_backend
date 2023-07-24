from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.dashboard.entities import BaseDashboardRepo


class Link(Model):
    """
    Ссылка
    """
    link: str = fields.TextField(description="Ссылка", null=True)
    element: fields.ForeignKeyRelation["Element"] = fields.ForeignKeyField(
        model_name="models.Element",
        related_name="links",
        on_delete=fields.CASCADE,
        description="Элемент",
        null=True,
    )
    city: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="links",
        on_delete=fields.CASCADE,
        description="Город",
        through="dashboard_link_city_through",
        backward_key="link_id",
        forward_key="city_id",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    def __str__(self) -> str:
        return self.link

    class Meta:
        table = "dashboard_link"


class LinkRepo(BaseDashboardRepo, CRUDMixin):
    """
    Репозиторий ссылки
    """
    model = Link

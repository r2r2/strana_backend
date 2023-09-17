from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceCategory(BaseAdditionalServiceDatabaseModel):
    """
    Категория (вид) услуги
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Название", max_length=150)
    priority: int = fields.IntField(default=0, description="Приоритет")
    active: bool = fields.BooleanField(description="Активность", default=True)
    service_categories: fields.ReverseRelation["AdditionalService"]

    class Meta:
        table = "additional_services_category"


class AdditionalServiceCategoryRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий категории услуг
    """

    model = AdditionalServiceCategory

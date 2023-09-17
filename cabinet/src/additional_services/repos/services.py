from tortoise import fields

from common import cfields
from common.orm.mixins import ReadWriteMixin

from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalService(BaseAdditionalServiceDatabaseModel):
    """
    Доп услуга
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Название", max_length=150)
    priority: int = fields.IntField(default=0, description="Приоритет")
    image_preview = cfields.MediaField(
        description="Превью изображения", max_length=300, null=True
    )
    image_detailed = cfields.MediaField(
        description="Детальное изображение", max_length=300, null=True
    )
    announcement: str = fields.TextField(description="Анонс")
    description: str = fields.TextField(description="Подробная информация")
    condition = fields.ForeignKeyField(
        model_name="models.AdditionalServiceCondition",
        related_name="service_condition",
        null=True,
        on_delete=fields.SET_NULL,
    )
    category = fields.ForeignKeyField(
        model_name="models.AdditionalServiceCategory",
        related_name="service_categories",
        null=True,
        on_delete=fields.SET_NULL,
    )
    active: bool = fields.BooleanField(description="Активность", default=True)
    group_status = fields.ForeignKeyField(
        model_name="models.AmocrmGroupStatus",
        related_name="service_group_status",
        null=True,
        on_delete=fields.SET_NULL,
    )
    hint: str = fields.TextField(description="Текст подсказки")
    kind = fields.ForeignKeyField(
        model_name="models.AdditionalServiceType",
        related_name="service_type",
        null=True,
        on_delete=fields.SET_NULL,
    )

    class Meta:
        table = "additional_services_service"


class AdditionalServiceRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий доп услуги
    """

    model = AdditionalService

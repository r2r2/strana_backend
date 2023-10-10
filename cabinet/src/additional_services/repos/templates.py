from tortoise import fields

from common.orm.mixins import ReadWriteMixin

from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceTemplate(BaseAdditionalServiceDatabaseModel):
    """
    Шаблоны доп услуг
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Название", max_length=150)
    description: str = fields.TextField(description="Текст")
    button_text: str = fields.TextField(description="Текст кнопки")
    slug: str = fields.CharField(
        max_length=50, description="slug", null=True, unique=True
    )

    class Meta:
        table = "additional_services_templates"


class AdditionalServiceTemplatetRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий шаблонов доп услуг
    """

    model = AdditionalServiceTemplate

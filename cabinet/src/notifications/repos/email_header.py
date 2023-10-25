from common import orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from common.models import TimeBasedMixin

from ..entities import BaseNotificationRepo


class EmailHeaderTemplate(Model, TimeBasedMixin):
    """
    Шаблоны хэдеров писем.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    text: str = fields.TextField(description="Текст шаблона хэдера письма")
    description: str = fields.TextField(description="Описание назначения шаблона хэдера письма", null=True)
    slug: str = fields.CharField(
        description="Слаг шаблона хэдера письма",
        max_length=100,
        unique=True,
    )
    is_active = fields.BooleanField(
        description="Шаблон хэдера активен",
        default=True,
    )

    class Meta:
        table = "notifications_email_headers"


class EmailHeaderTemplateRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий шаблонов хэдеров писем.
    """
    model = EmailHeaderTemplate
    q_builder: orm.QBuilder = orm.QBuilder(EmailHeaderTemplate)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(EmailHeaderTemplate)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(EmailHeaderTemplate)

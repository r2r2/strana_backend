from common import orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from common.models import TimeBasedMixin

from ..entities import BaseNotificationRepo


class EmailFooterTemplate(Model, TimeBasedMixin):
    """
    Шаблоны футеров писем.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    text: str = fields.TextField(description="Текст шаблона футера письма")
    description: str = fields.TextField(description="Описание назначения шаблона футера письма", null=True)
    slug: str = fields.CharField(
        description="Слаг шаблона футера письма",
        max_length=100,
        unique=True,
    )
    is_active = fields.BooleanField(
        description="Шаблон футера активен",
        default=True,
    )

    class Meta:
        table = "notifications_email_footers"


class EmailFooterTemplateRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий шаблонов футеров писем.
    """
    model = EmailFooterTemplate
    q_builder: orm.QBuilder = orm.QBuilder(EmailFooterTemplate)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(EmailFooterTemplate)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(EmailFooterTemplate)

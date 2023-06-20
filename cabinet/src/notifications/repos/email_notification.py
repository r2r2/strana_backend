from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from common.models import TimeBasedMixin

from ..entities import BaseNotificationRepo


class EmailTemplateLkType(mixins.Choices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class EmailTemplate(Model, TimeBasedMixin):
    """
    Шаблоны писем.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    template_topic: str = fields.TextField(description="Заголовок шаблона письма")
    template_text: str = fields.TextField(description="Текст шаблона письма")
    lk_type: str = cfields.CharChoiceField(
        description="Сервис ЛК, в котором применяется шаблон",
        max_length=10,
        choice_class=EmailTemplateLkType,
    )
    mail_event: str = fields.TextField(description="Описание назначения события отправки письма", null=True)
    mail_event_slug: str = fields.CharField(
        description="Слаг назначения события отправки письма",
        max_length=100,
        unique=True,
    )
    is_active = fields.BooleanField(
        description="Шаблон активен",
        default=True,
    )

    class Meta:
        table = "notifications_email_notification"


class EmailTemplateRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий шаблонов писем.
    """
    model = EmailTemplate
    q_builder: orm.QBuilder = orm.QBuilder(EmailTemplate)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(EmailTemplate)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(EmailTemplate)

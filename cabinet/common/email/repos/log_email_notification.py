from common import orm
from tortoise import Model, fields

from ...orm.mixins import CRUDMixin
from ...models import TimeBasedMixin
from ...entities import BaseRepo


class LogEmail(Model, TimeBasedMixin):
    """
    Логи отправленных писем.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    topic: str = fields.TextField(
        description="Заголовок письма",
        null=True,
    )
    text: str = fields.TextField(
        description="Текст письма",
        null=True,
    )
    lk_type: str = fields.CharField(
        description="Сервис ЛК, в котором отправлено письмо",
        max_length=10,
        null=True,
    )
    mail_event_slug: str = fields.CharField(
        description="Слаг назначения события отправки письма",
        max_length=100,
        null=True,
    )
    recipient_emails = fields.TextField(
        description="Почтовые адреса получателей письма",
        null=True,
    )
    is_sent = fields.BooleanField(
        description="Письмо отправлено",
        default=False,
    )

    class Meta:
        table = "common_log_email_notification"


class LogEmailRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий логов отправленных писем.
    """
    model = LogEmail
    q_builder: orm.QBuilder = orm.QBuilder(LogEmail)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(LogEmail)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(LogEmail)

from common import orm
from tortoise import Model, fields

from ...orm.mixins import CRUDMixin
from ...models import TimeBasedMixin
from ...entities import BaseRepo


class LogSms(Model, TimeBasedMixin):
    """
    Логи отправленных cмс сообщений.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    text: str = fields.TextField(
        description="Текст смс сообщения",
        null=True,
    )
    lk_type: str = fields.CharField(
        description="Сервис ЛК, в котором отправлено смс сообщение",
        max_length=10,
        null=True,
    )
    sms_event_slug: str = fields.CharField(
        description="Слаг назвачения события отправки смс",
        max_length=100,
        null=True,
    )
    recipient_phone = fields.CharField(
        description="Номер телефона получателя",
        max_length=20,
        null=True,
    )
    is_sent = fields.BooleanField(
        description="Сообщение отправлено",
        default=False,
    )

    class Meta:
        table = "common_log_sms_notification"


class LogSmsRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий логов отправленных смс сообщений.
    """
    model = LogSms
    q_builder: orm.QBuilder = orm.QBuilder(LogSms)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(LogSms)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(LogSms)

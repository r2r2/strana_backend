from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from common.models import TimeBasedMixin

from ..entities import BaseNotificationRepo


class SmsTemplateLkType(mixins.Choices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class SmsTemplate(Model, TimeBasedMixin):
    """
    Шаблоны cмс сообщений.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    template_text: str = fields.TextField(description="Текст шаблона смс сообщения")
    lk_type: str = cfields.CharChoiceField(
        description="Сервис ЛК, в котором применяется шаблон",
        max_length=10,
        choice_class=SmsTemplateLkType,
        null=True,
    )
    sms_event: str = fields.TextField(description="Описание назначения события отправки смс", null=True)
    sms_event_slug: str = fields.TextField(description="Слаг события отправки смс", max_length=100)
    is_active = fields.BooleanField(
        description="Шаблон активен",
        default=True,
    )

    class Meta:
        table = "notifications_sms_notification"


class SmsTemplateRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий шаблонов смс сообщений.
    """
    model = SmsTemplate
    q_builder: orm.QBuilder = orm.QBuilder(SmsTemplate)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(SmsTemplate)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(SmsTemplate)

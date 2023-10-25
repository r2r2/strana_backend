from tortoise import Model, fields

from common import cfields, mixins
from common.orm.mixins import CRUDMixin
from src.notifications.entities import BaseNotificationRepo


class EventsSmsNotificationType(mixins.Choices):
    """
    Типы уведомление для брокеров, участвующих в мероприятиях.
    """

    BEFORE: tuple = "before", "До мероприятия"
    AFTER: tuple = "after", "После окончания мероприятия"


class EventsSmsNotification(Model):
    """
    Уведомление для брокеров, участвующих в мероприятиях.
    """

    id: int = fields.IntField(description="ID", pk=True)
    sms_template: fields.ForeignKeyNullableRelation["SmsTemplate"] = fields.ForeignKeyField(
        model_name="models.SmsTemplate",
        on_delete=fields.CASCADE,
        related_name="event_sms_notifications",
        description="Шаблон смс",
        null=True,
    )
    sms_event_type: bool = cfields.CharChoiceField(
        description="Тип события отправки смс",
        null=True,
        max_length=100,
        choice_class=EventsSmsNotificationType,
    )
    cities: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="event_sms_notifications",
        through="notifications_event_sms_notifications_city_through",
        description="Города",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="event_sms_notification_id",
        forward_key="city_id",
    )
    days: float = fields.FloatField(
        description="За сколько дней до события / после события отправлять",
        null=True,
    )
    only_for_online: bool = fields.BooleanField(description="Только для онлайн мероприятий", default=False)

    class Meta:
        table = "notifications_event_sms_notification"


class EventsSmsNotificationCityThrough(Model):
    """
    Проекты, для которых настроено уведомление для брокеров, участвующих в мероприятиях.
    """

    event_sms_notification: fields.ForeignKeyRelation[EventsSmsNotification] = fields.ForeignKeyField(
        model_name="models.EventsSmsNotification",
        related_name="city_through",
        description="Уведомление для брокеров, участвующих в мероприятиях",
        on_delete=fields.CASCADE,
    )
    city: fields.ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name="models.City",
        related_name="event_sms_notification_through",
        description="Город",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "notifications_event_sms_notifications_city_through"


class EventsSmsNotificationRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий уведомлений для брокеров, участвующих в мероприятиях.
    """

    model = EventsSmsNotification

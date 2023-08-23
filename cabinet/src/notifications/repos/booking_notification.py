from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.booking.constants import BookingCreatedSources
from src.notifications.entities import BaseNotificationRepo


class BookingNotification(Model):
    """
    Уведомление при платном бронировании
    """
    id: int = fields.IntField(description="ID", pk=True)
    sms_template: fields.ForeignKeyNullableRelation["SmsTemplate"] = fields.ForeignKeyField(
        model_name="models.SmsTemplate",
        on_delete=fields.CASCADE,
        related_name="booking_notifications",
        description="Шаблон смс уведомления",
        null=True,
    )
    created_source: bool = cfields.CharChoiceField(
        description="Источник создания онлайн-бронирования",
        null=True,
        max_length=100,
        choice_class=BookingCreatedSources,
    )
    project: fields.ManyToManyRelation["Project"] = fields.ManyToManyField(
        model_name="models.Project",
        related_name="booking_notifications",
        through="booking_notifications_project_through",
        description="ЖК",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="booking_notification_id",
        forward_key="project_id",
    )
    hours_before_send: float = fields.FloatField(
        description="За сколько часов до момента окончания резервирования отправлять (ч)",
        null=True,
    )

    class Meta:
        table = "booking_notifications"


class BookingNotificationsProjectThrough(Model):
    """
    Проекты, для которых настроено уведомление при платном бронировании
    """
    booking_notification: fields.ForeignKeyRelation[BookingNotification] = fields.ForeignKeyField(
        model_name="models.BookingNotification",
        related_name="project_through",
        description="Уведомление при платном бронировании",
        on_delete=fields.CASCADE,
    )
    project: fields.ForeignKeyRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        related_name="booking_notification_through",
        description="Проект (ЖК)",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "booking_notifications_project_through"


class BookingNotificationRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий уведомлений при платном бронировании
    """
    model = BookingNotification

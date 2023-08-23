from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.booking.constants import BookingFixationNotificationType
from src.notifications.entities import BaseNotificationRepo


class BookingFixationNotification(Model):
    """
    Уведомление при окончании фиксации.
    """
    id: int = fields.IntField(description="ID", pk=True)
    mail_template: fields.ForeignKeyNullableRelation["EmailTemplate"] = fields.ForeignKeyField(
        model_name="models.EmailTemplate",
        on_delete=fields.CASCADE,
        related_name="booking_fixation_notifications",
        description="Шаблон письма",
        null=True,
    )
    type: bool = cfields.CharChoiceField(
        description="Тип события",
        null=True,
        max_length=100,
        choice_class=BookingFixationNotificationType,
    )
    project: fields.ManyToManyRelation["Project"] = fields.ManyToManyField(
        model_name="models.Project",
        related_name="booking_fixation_notifications",
        through="booking_fixation_notifications_project_through",
        description="ЖК",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="booking_fixation_notification_id",
        forward_key="project_id",
    )
    days_before_send: float = fields.FloatField(
        description="За сколько дней до события отправлять",
        null=True,
    )

    class Meta:
        table = "booking_fixation_notifications"


class BookingFixationNotificationsProjectThrough(Model):
    """
    Проекты, для которых настроено уведомление при окончании фиксации.
    """
    booking_fixation_notification: fields.ForeignKeyRelation[BookingFixationNotification] = fields.ForeignKeyField(
        model_name="models.BookingFixationNotification",
        related_name="project_through",
        description="Уведомление при окончании фиксации",
        on_delete=fields.CASCADE,
    )
    project: fields.ForeignKeyRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        related_name="booking_fixation_notification_through",
        description="Проект (ЖК)",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "booking_fixation_notifications_project_through"


class BookingFixationNotificationRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий уведомлений при платном бронировании
    """
    model = BookingFixationNotification

from datetime import datetime

from tortoise import Model, fields

from common import cfields, mixins
from common.orm.mixins import CRUDMixin
from src.notifications.entities import BaseNotificationRepo


class QRcodeSMSNotifyType(mixins.Choices):
    """
    Типы уведомление о QR-коде для смс.
    """

    BEFORE: tuple = "before", "До мероприятия"
    AFTER: tuple = "after", "После окончания мероприятия"


class QRcodeSMSNotify(Model):
    """
    Уведомление о QR-коде для смс.
    """

    id: int = fields.IntField(description="ID", pk=True)
    sms_template: fields.ForeignKeyNullableRelation["SmsTemplate"] = fields.ForeignKeyField(
        model_name="models.SmsTemplate",
        on_delete=fields.CASCADE,
        related_name="qrcode_sms",
        description="Шаблон смс",
        null=True,
    )
    sms_event_type: bool = cfields.CharChoiceField(
        description="Тип события отправки смс",
        null=True,
        max_length=100,
        choice_class=QRcodeSMSNotifyType,
    )
    cities: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="qrcode_sms",
        through="notifications_qrcode_sms_city_through",
        description="Города",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="qrcode_sms_id",
        forward_key="city_id",
    )
    events: fields.ManyToManyRelation["EventList"] = fields.ManyToManyField(
        model_name="models.EventList",
        related_name="qrcode_sms",
        through="notifications_qrcode_sms_eventlist_through",
        description="Мероприятия",
        null=True,
        on_delete=fields.SET_NULL,
        backward_key="qrcode_sms_id",
        forward_key="event_id",
    )

    days_before_send: float = fields.FloatField(
        description="За сколько дней до события отправлять",
        null=True,
    )
    time_to_send: datetime.time = fields.TimeField(
        description="Время отправки",
        null=True,
    )

    class Meta:
        table = "notifications_qrcode_sms"


class QRcodeSMSCityThrough(Model):
    """
    Проекты, для которых настроено уведомление о QR-коде для смс.
    """
    id: int = fields.IntField(description="ID", pk=True)
    qrcode_sms: fields.ForeignKeyRelation[QRcodeSMSNotify] = fields.ForeignKeyField(
        model_name="models.QRcodeSMSNotify",
        related_name="city_through",
        description="Уведомление о QR-коде для смс",
        on_delete=fields.CASCADE,
    )
    city: fields.ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name="models.City",
        related_name="qrcode_sms_through",
        description="Город",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "notifications_qrcode_sms_city_through"


class QRcodeSMSEventListThrough(Model):
    """
    Мероприятия, для которых настроено уведомление о QR-коде для смс.
    """
    id: int = fields.IntField(description="ID", pk=True)
    qrcode_sms: fields.ForeignKeyRelation[QRcodeSMSNotify] = fields.ForeignKeyField(
        model_name="models.QRcodeSMSNotify",
        related_name="eventlist_through",
        description="Уведомление о QR-коде для смс",
        on_delete=fields.CASCADE,
    )
    event: fields.ForeignKeyRelation["EventList"] = fields.ForeignKeyField(
        model_name="models.EventList",
        related_name="qrcode_sms_through",
        description="Мероприятие",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "notifications_qrcode_sms_eventlist_through"


class QRcodeSMSNotifyRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий уведомления о QR-коде для смс.
    """
    model = QRcodeSMSNotify

from datetime import datetime

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.notifications.entities import BaseNotificationRepo


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
    groups: fields.ManyToManyRelation["EventGroup"] = fields.ManyToManyField(
        model_name="models.EventGroup",
        related_name="qrcode_sms",
        through="notifications_qrcode_sms_eventgroup_through",
        description="Группы",
        null=True,
        on_delete=fields.SET_NULL,
        backward_key="qrcode_sms_id",
        forward_key="event_group_id",
    )
    time_to_send: datetime = fields.DatetimeField(
        description="Дата и время отправки смс",
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


class QRCodeSMSGroupThrough(Model):
    """
    Группы, для которых настроено уведомление о QR-коде для смс.
    """
    id: int = fields.IntField(description="ID", pk=True)
    qrcode_sms: fields.ForeignKeyRelation[QRcodeSMSNotify] = fields.ForeignKeyField(
        model_name="models.QRcodeSMSNotify",
        related_name="group_through",
        description="Уведомление о QR-коде для смс",
        on_delete=fields.CASCADE,
    )
    event_group: fields.ForeignKeyRelation["EventGroup"] = fields.ForeignKeyField(
        model_name="models.EventGroup",
        related_name="qrcode_sms_through",
        description="Группа",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "notifications_qrcode_sms_eventgroup_through"


class QRcodeSMSNotifyRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий уведомления о QR-коде для смс.
    """
    model = QRcodeSMSNotify

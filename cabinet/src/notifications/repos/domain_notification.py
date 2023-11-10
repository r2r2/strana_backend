from datetime import datetime
from typing import Optional

from tortoise import Model, fields

from common.orm.mixins import ReadWriteMixin, CountMixin
from ..entities import BaseNotificationRepo


class Onboarding(Model):
    """
    Уведомления онбординга
    """
    id: int = fields.BigIntField(description="ID", pk=True, index=True)
    message: str = fields.TextField(description="Сообщение")
    slug: str = fields.CharField(description="Слаг", max_length=50)
    button_text: str = fields.CharField(description="Текс кнопки", max_length=150)

    user: fields.ManyToManyRelation["User"] = fields.ManyToManyField(
        model_name="models.User",
        related_name="booking_clients",
        through="notifications_onboarding_user_through",
        description="Пользователи",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="onboarding_id",
        forward_key="user_id",
    )

    def __str__(self) -> str:
        return f"Онбординг #{self.slug}"

    class Meta:
        table = "notifications_onboarding"


class OnboardingUserThrough(Model):
    """
    Уведомления онбординга конкретного пользователя
    """

    onboarding: fields.ForeignKeyRelation[Onboarding] = fields.ForeignKeyField(
        model_name="models.Onboarding",
        related_name="user_through",
        description="Уведомления онбординга",
        on_delete=fields.CASCADE,
    )
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        related_name="onboarding_through",
        description="Клиент",
        on_delete=fields.CASCADE,
    )
    is_read: bool = fields.BooleanField(description="Прочитано", default=False)
    is_sent: bool = fields.BooleanField(description="Отправлено", default=False)
    sent: Optional[datetime] = fields.DatetimeField(description="Время отправления", null=True)
    read: Optional[datetime] = fields.DatetimeField(description="Время просмотра", null=True)

    class Meta:
        table = "notifications_onboarding_user_through"


class OnboardingUserThroughRepo(BaseNotificationRepo, ReadWriteMixin, CountMixin):
    """
    Репозиторий уведомлений онбординга конкретного пользователя
    """
    model = OnboardingUserThrough


class OnboardingRepo(BaseNotificationRepo, ReadWriteMixin, CountMixin):
    """
    Репозиторий уведомления
    """
    model = Onboarding

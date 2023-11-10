from datetime import datetime

from django.db import models

class Onboarding(models.Model):
    """
    Уведомления онбординга
    """
    message: str = models.TextField(verbose_name="Сообщение")
    slug: str = models.CharField(verbose_name="Слаг", max_length=50)
    button_text: str = models.CharField(verbose_name="Текс кнопки", max_length=150)

    user: models.ForeignKey = models.ManyToManyField(
        to="users.CabinetUser",
        related_name="booking_clients",
        through="OnboardingUserThrough",
        verbose_name="Пользователи",
        blank=True,
        through_fields=("onboarding", "user"),
    )

    def __str__(self) -> str:
        return f"Онбординг #{self.slug}"

    class Meta:
        managed = False
        db_table = "notifications_onboarding"
        verbose_name = 'Онбординг'
        verbose_name_plural = '5.5 Онбординг'


class OnboardingUserThrough(models.Model):
    """
    Уведомления онбординга конкретного пользователя
    """

    onboarding: models.ForeignKey = models.OneToOneField(
        to="contents.Onboarding",
        related_name="user_through",
        verbose_name="Уведомления онбординга",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    user: models.ForeignKey = models.ForeignKey(
        to="users.CabinetUser",
        related_name="onboarding_through",
        verbose_name="Клиент",
        on_delete=models.CASCADE,
    )
    is_read: bool = models.BooleanField(verbose_name="Прочитано", default=False)
    is_sent: bool = models.BooleanField(verbose_name="Отправлено", default=False)
    sent: datetime | None = models.DateTimeField(verbose_name="Время отправления", null=True)
    read: datetime | None = models.DateTimeField(verbose_name="Время просмотра", null=True)

    class Meta:
        managed = False
        db_table = "notifications_onboarding_user_through"
        verbose_name = 'Связь онбординга и пользователя'
        verbose_name_plural = 'Связи онбордингов и пользователей'

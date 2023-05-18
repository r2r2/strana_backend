from django.db import models


class AgencyAdditionalAgreement(models.Model):
    """
    Дополнительное соглашение к договору агентства
    """
    number = models.CharField(
        max_length=50,
        verbose_name="Номер документа",
        help_text="Номер документа (максимум 50 символов)",
        blank=True,
        null=True,
    )
    status = models.ForeignKey(
        "agreements.AdditionalAgreementStatus",
        models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Статус",
        help_text="Статус",
    )
    template_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Название шаблона",
        help_text="Шаблон документа в АМО, задается при формировании договора"
    )
    files = models.JSONField(verbose_name="Файлы", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)
    agency = models.ForeignKey(
        "agencies.Agency",
        models.CASCADE,
        related_name='additional_agreements',
        verbose_name='Агенство',
        help_text='Агенство'
    )
    project = models.ForeignKey(
        "projects.Project",
        models.CASCADE,
        verbose_name="Проект",
        help_text="Проект"
    )
    booking = models.ForeignKey(
        "booking.Booking",
        models.SET_NULL,
        verbose_name="Бронь",
        help_text="Бронь",
        null=True,
        blank=True,
    )
    reason_comment = models.CharField(
        max_length=200,
        verbose_name="Комментарий",
        help_text="Комментарий (администратора)"
    )
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Когда подписано",
        help_text="Когда подписано"
    )

    def __str__(self):
        return f"№ {self.number}"

    class Meta:
        managed = False
        db_table = "agencies_additional_agreement"
        verbose_name = "Дополнительное соглашение"
        verbose_name_plural = "Дополнительные соглашения"

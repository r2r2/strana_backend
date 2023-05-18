from django.db import models


class BaseAgreement(models.Model):
    """
    Базовая модель для договора и актов агентств
    """

    number = models.CharField(
        max_length=50,
        verbose_name="Номер документа",
        help_text="Номер документа (максимум 50 символов)"
    )
    status = models.ForeignKey(
        "agreements.AgreementStatus",
        models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Статус",
        help_text="Статус",
    )
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Когда подписано",
        help_text="Когда подписано"
    )
    template_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Название шаблона",
        help_text="Название шаблона"
    )
    files = models.JSONField(verbose_name="Файлы", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self):
        return f"№ {self.number}"

    class Meta:
        managed = False
        abstract = True

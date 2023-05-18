# pylint: disable=invalid-str-returned
from django.db import models
from django.utils.translation import gettext_lazy as _


class AdditionalAgreementType(models.TextChoices):
    OOO: str = "OOO", _("ООО")
    IP: str = "IP", _("ИП")


class AdditionalAgreementTemplate(models.Model):
    """
    Модель шаблонов дополнительных соглашений
    """

    project = models.ForeignKey(
        "projects.Project",
        models.CASCADE,
        related_name="additional_templates",
        verbose_name="ЖК",
    )
    template_name: str = models.CharField(
        verbose_name='Название шаблона',
        max_length=150,
        help_text="Название шаблона")
    type: str = models.CharField(
        verbose_name="Тип организации",
        choices=AdditionalAgreementType.choices,
        max_length=10,
        null=False,
    )

    def __str__(self):
        return self.template_name

    class Meta:
        managed = False
        db_table = "additional_agreement_templates"
        verbose_name = "Шаблон дополнительного соглашения"
        verbose_name_plural = "Шаблоны дополнительных соглашений"

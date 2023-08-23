# pylint: disable=invalid-str-returned
from django.db import models
from django.utils.translation import gettext_lazy as _


class AgreementType(models.TextChoices):
    OOO: str = "OOO", _("ООО")
    IP: str = "IP", _("ИП")


class DocTemplate(models.Model):
    """
    Модель шаблонов договоров
    """

    project = models.ForeignKey(
        "properties.Project",
        models.CASCADE,
        related_name="templates",
        verbose_name="ЖК",
    )
    agreement_type = models.ForeignKey(
        "documents.AgreementType",
        models.CASCADE,
        related_name="templates",
        verbose_name="Тип документа",
    )
    type: str = models.CharField(
        verbose_name="Тип организации",
        choices=AgreementType.choices,
        max_length=10,
        null=False,
    )
    template_name: str = models.CharField(
        verbose_name='Название шаблона',
        max_length=150,
        help_text="Название шаблона должно соответствовать названию документа в АМО и включать формат [.docx], "
                  "например (Договор.docx)”",
    )

    def __str__(self):
        return self.template_name

    class Meta:
        managed = False
        db_table = "docs_templates"
        verbose_name = "Шаблон договора"
        verbose_name_plural = " 7.8. [Справочник] Шаблоны договоров в АМО"

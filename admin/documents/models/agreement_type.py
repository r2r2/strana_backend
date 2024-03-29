# pylint: disable=invalid-str-returned
from typing import Optional

from django.db import models


class AgreementType(models.Model):
    """
    Типы документов
    """

    name: str = models.CharField(verbose_name='Тип документа', max_length=100)
    description: Optional[str] = models.TextField(
        verbose_name='Описание типа',
        blank=True,
        null=True,
        help_text="Используется в подсказке к статусу при формирование договора",
    )
    priority: int = models.IntegerField(
        verbose_name="Приоритет",
        null=False,
        help_text="Чем меньше приоритет, тем раньше в списке выводится тип ДС в списке",
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда изменено", editable=False, auto_now=True)
    created_by = models.ForeignKey(
        "users.User",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_agreement_types",
        verbose_name="Кем создано",
        editable=False,
    )
    updated_by = models.ForeignKey(
        "users.User",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="updated_agreement_types",
        verbose_name="Кем изменено",
        editable=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "agreement_type"
        verbose_name = "Тип договора"
        verbose_name_plural = " 7.6. [Справочник] Типы договоров"

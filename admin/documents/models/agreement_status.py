# pylint: disable=invalid-str-returned
from typing import Optional

from django.db import models


class AgreementStatus(models.Model):
    """
    Статусы документов
    """

    name: str = models.CharField(verbose_name='Название статуска', max_length=100)
    description: Optional[str] = models.TextField(
        verbose_name='Описание статуса',
        help_text="Используется в подсказке к статусу при формирование договора",
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "agreement_status"
        verbose_name = "Статус договора"
        verbose_name_plural = " 7.4. [Справочник] Статусы договоров"

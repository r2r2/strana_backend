# pylint: disable=invalid-str-returned
from typing import Optional

from django.db import models


class AdditionalAgreementStatus(models.Model):
    """
    Статусы дополнительных соглашений
    """

    name: str = models.CharField(verbose_name='Название статуса', max_length=100)
    description: Optional[str] = models.TextField(
        verbose_name='Описание статуса',
        help_text="Используется в подсказке к статусу при формирование договора",
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "additional_agreement_status"
        verbose_name = "Статус дополнительного соглашения"
        verbose_name_plural = " 7.5. [Справочник] Статусы дополнительных соглашений"

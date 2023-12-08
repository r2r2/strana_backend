from django.db import models


class RopEmailsDispute(models.Model):
    """
    Таблица с почтами Руководителей отдела продаж, не путать с юзерами типа роп
    """

    fio: str = models.CharField(verbose_name="ФИО ропа", max_length=100)
    project = models.ForeignKey(
        verbose_name="Проект",
        to="properties.Project",
        related_name="project_rop",
        on_delete=models.CASCADE,
    )
    email: str = models.CharField(
        verbose_name="Email", max_length=100
    )

    class Meta:
        managed = False
        db_table = "notifications_rop_emails_dispute"
        verbose_name = "Роп (для писем оспаривания)"
        verbose_name_plural = ' 4.11 Ропы (для писем оспаривания)'

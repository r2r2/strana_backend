from django.db import models


class AmocrmPipeline(models.Model):
    """
    Таблица воронок из AmoCRM
    """
    id = models.IntegerField(primary_key=True, verbose_name="ID воронки из AmoCRM")
    name = models.CharField(verbose_name="Название воронки", max_length=150)
    sort = models.IntegerField(verbose_name="Сортировка", default=0)
    is_archive = models.BooleanField(verbose_name="В архиве", default=False)
    is_main = models.BooleanField(verbose_name="Основная воронка", default=False)
    account_id = models.IntegerField(verbose_name="ID аккаунта", null=True, blank=True)
    city = models.ForeignKey(
        "references.Cities",
        verbose_name="Город",
        related_name='pipelines',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} | {self.id}"

    class Meta:
        managed = False
        db_table = "amocrm_pipelines"
        verbose_name = "Воронка"
        verbose_name_plural = " 1.2. [Справочник] Воронки из АМО"

from django.db import models


class SystemList(models.Model):
    """
    Список систем
    """
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Название",
    )
    slug = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Слаг",
    )

    def __str__(self) -> str:
        return self.name if self.name else str(self.id)

    class Meta:
        managed = False
        db_table = 'settings_system_list'
        verbose_name = "Список систем"
        verbose_name_plural = "15.4 [Справочник] Список систем"

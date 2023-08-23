from django.db import models


class TaskField(models.Model):
    """
    Поля заданий
    """
    name: str = models.CharField(max_length=100, verbose_name="Название поля")
    type: str = models.CharField(max_length=100, verbose_name="Тип поля", null=True, blank=True)
    field_name: str = models.CharField(max_length=100, verbose_name="Название поля в БД")

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = "task_management_taskfields"
        verbose_name = "Поле задания"
        verbose_name_plural = "9.5. Поля заданий"


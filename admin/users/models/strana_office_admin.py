from django.db import models


class StranaOfficeAdmin(models.Model):
    """
    Администратор офиса "Страна"
    """

    fio: str = models.CharField(verbose_name="ФИО админа", max_length=100)
    project = models.ForeignKey(
        verbose_name="Проект",
        to="properties.Project",
        related_name="project_admin",
        on_delete=models.CASCADE,
    )
    email: str = models.CharField(
        verbose_name="Email", max_length=100
    )

    class Meta:
        managed = False
        db_table = "users_strana_office_admin"
        verbose_name = "Администратор офиса"
        verbose_name_plural = '2.12. Администратор офиса "Страна"'

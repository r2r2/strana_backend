from django.db import models

from django.utils.translation import gettext_lazy as _


class MeetingType(models.TextChoices):
    """
    Тип встречи
    """
    ONLINE: str = "kc", _("Онлайн")
    OFFLINE: str = "meet", _("Офлайн")


class StranaOfficeAdmin(models.Model):
    """
    Администратор офиса "Страна"
    """

    fio: str = models.CharField(verbose_name="ФИО админа", max_length=100)
    projects = models.ManyToManyField(
        to="properties.Project",
        related_name="project_admin",
        verbose_name="Проекты",
        blank=True,
        through="StranaOfficeAdminsProjectsThrough",
    )
    email: str = models.CharField(
        verbose_name="Email", max_length=100
    )
    type: str = models.CharField(
        verbose_name="Тип встречи",
        max_length=20,
        choices=MeetingType.choices,
        default=MeetingType.ONLINE,
    )

    class Meta:
        managed = False
        db_table = "users_strana_office_admin"
        verbose_name = "Администратор офиса"
        verbose_name_plural = '2.12. Администратор офиса "Страна"'


class StranaOfficeAdminsProjectsThrough(models.Model):
    """
    Матрица условий закрепления
    """
    strana_office_admin = models.ForeignKey(
        to="StranaOfficeAdmin",
        on_delete=models.CASCADE,
        verbose_name="Админ",
        related_name="strana_office_admin_project_through",
        primary_key=True,
    )
    project = models.ForeignKey(
        "properties.Project",
        on_delete=models.CASCADE,
        verbose_name="Проект",
        related_name="project_strana_office_admin_through",
    )

    class Meta:
        managed = False
        db_table = "users_strana_office_admins_project_through"

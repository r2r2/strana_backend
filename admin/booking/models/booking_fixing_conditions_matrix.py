from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingFixingConditionsMatrix(models.Model):
    """
    Матрица условий закрепления
    """
    class BookingCreatedSources(models.TextChoices):
        """
        Источники создания бронирования
        """
        LK_ASSIGN = "lk_booking_assign", _("Закреплен в ЛК Брокера")

    project = models.ManyToManyField(
        to="properties.Project",
        related_name="condition_projects",
        verbose_name="Проекты",
        blank=True,
        through="BookingFixingConditionsMatrixProjects",
    )
    created_source = models.CharField(
        choices=BookingCreatedSources.choices,
        default=BookingCreatedSources.LK_ASSIGN,
        max_length=100,
        verbose_name="Источник создания онлайн-бронирования",
    )
    status_on_create = models.ForeignKey(
        "booking.AmocrmGroupStatus",
        on_delete=models.SET_NULL,
        related_name='condition_statuses',
        verbose_name="Статус создаваемой сделки",
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "booking_fixing_conditions_matrix"
        verbose_name = "Матрица условий закрепления"
        verbose_name_plural = " 1.8. [Справочник] Матрица условий закрепления"


class BookingFixingConditionsMatrixProjects(models.Model):
    """
    Матрица условий закрепления
    """
    fixing_conditions_matrix = models.ForeignKey(
        "BookingFixingConditionsMatrix",
        on_delete=models.CASCADE,
        verbose_name="Матрица условий закрепления",
        related_name="booking_project_matrix",
    )
    project = models.ForeignKey(
        "properties.Project",
        on_delete=models.CASCADE,
        verbose_name="Проект",
        related_name="booking_fixing_condition_matrix",
    )

    class Meta:
        managed = False
        db_table = "booking_fixing_conditions_matrix_projects"

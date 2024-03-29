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
    consultation_type = models.ForeignKey(
        "disputes.ConsultationType",
        on_delete=models.SET_NULL,
        related_name='fixing_conditions',
        verbose_name="Тип консультации",
        blank=True,
        null=True,
    )
    status_on_create = models.ForeignKey(
        "booking.AmocrmGroupStatus",
        on_delete=models.SET_NULL,
        related_name='condition_statuses',
        verbose_name="Статус создаваемой сделки",
        blank=True,
        null=True,
    )
    pipeline = models.ManyToManyField(
        verbose_name="Воронки",
        to="booking.AmocrmPipeline",
        through="BookingFixingConditionsMatrixPipelineThrough",
        blank=True,
    )
    amo_responsible_user_id: str | None = models.CharField(
        verbose_name="ID ответственного в AmoCRM", max_length=200, null=True, blank=True
    )
    priority: int = models.IntegerField(
        verbose_name="Приоритет",
        null=False,
        help_text="Чем меньше приоритет тем раньше проверяется условие",
    )

    class Meta:
        managed = False
        db_table = "booking_fixing_conditions_matrix"
        verbose_name = "Матрица условий закрепления"
        verbose_name_plural = " 1.8. [Справочник] Матрица условий закрепления"
        ordering = ["priority"]


class BookingFixingConditionsMatrixPipelineThrough(models.Model):

    pipeline = models.ForeignKey(
        verbose_name="Воронка",
        to="booking.AmocrmPipeline",
        on_delete=models.CASCADE,
        unique=False,
    )

    booking_fixing_conditions_matrix = models.ForeignKey(
        "BookingFixingConditionsMatrix",
        on_delete=models.CASCADE,
        verbose_name="Матрица условий закрепления",
        related_name="pipelines",
    )

    class Meta:
        managed = False
        db_table = "booking_fixing_conditions_matrix_pipeline_through"
        unique_together = (('pipeline', 'booking_fixing_conditions_matrix'),)


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

from django.db import models


class AgencyAdditionalAgreementCreatingData(models.Model):
    """
    Данные для формирования ДС через админку.
    """
    projects = models.ManyToManyField(
        to="properties.Project",
        through="AdditionalProjectThrough",
        through_fields=("additional_data", "project"),
        related_name="additional_data",
        verbose_name="Проекты",
        help_text="Проекты для формирования ДС",
    )
    agencies = models.ManyToManyField(
        to="users.Agency",
        through="AdditionalAgencyThrough",
        through_fields=("additional_data", "agency"),
        related_name="additional_data",
        verbose_name="Агентства",
        help_text="Агентства для формирования ДС",
    )
    reason_comment = models.CharField(
        max_length=200,
        verbose_name="Комментарий",
        help_text="Комментарий (администратора)"
    )
    additionals_created = models.BooleanField(
        verbose_name="ДС сгенерированы",
        default=False,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name="Когда создано",
        help_text="Когда создано",
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return f"{self._meta.verbose_name}, id - {self.id}"

    class Meta:
        managed = False
        db_table = "agencies_additional_agreement_creating_data"
        verbose_name = "Данные для создания дополнительных соглашений"
        verbose_name_plural = "7.10. [Сервис] Создание дополнительных соглашений"


class AdditionalProjectThrough(models.Model):
    additional_data = models.OneToOneField(
        verbose_name="Данные ДС",
        to="documents.AgencyAdditionalAgreementCreatingData",
        on_delete=models.CASCADE,
        related_name="through_project",
        primary_key=True,
    )
    project = models.ForeignKey(
        verbose_name="Проект",
        to="properties.Project",
        on_delete=models.CASCADE,
        related_name="through_agency_data",
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "additional_data_projects"
        unique_together = ('additional_data', 'project')
        verbose_name = verbose_name_plural = "Данные ДС - Проект"


class AdditionalAgencyThrough(models.Model):
    additional_data = models.OneToOneField(
        verbose_name="Данные ДС",
        to="documents.AgencyAdditionalAgreementCreatingData",
        on_delete=models.CASCADE,
        related_name="through_agency",
        primary_key=True,
    )
    agency = models.ForeignKey(
        verbose_name="Агентство",
        to="users.Agency",
        on_delete=models.CASCADE,
        related_name="through_agency_data",
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "additional_data_agencies"
        unique_together = ('additional_data', 'agency')
        verbose_name = verbose_name_plural = "Данные ДС - Агентство"

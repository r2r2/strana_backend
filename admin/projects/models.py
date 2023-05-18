#pylint: disable=invalid-str-returned,no-member
from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    Проект
    """
    class Status(models.TextChoices):
        """
        Поля для статусов
        """
        CURRENT = "current", _("Текущий")
        COMPLETED = "completed", _("Завершённый")
        FUTURE = "future", _("Будущий")

    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey('cities.Cities', models.SET_NULL, blank=True, null=True)
    amocrm_enum = models.BigIntegerField(blank=True, null=True)
    amocrm_name = models.CharField(max_length=200, blank=True, null=True)
    amocrm_organization = models.CharField(max_length=200, blank=True, null=True)
    amo_responsible_user_id = models.CharField(max_length=200, blank=True, null=True)
    amo_pipeline_id = models.CharField(max_length=200, blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField()
    priority = models.IntegerField()
    status = models.CharField(
        choices=Status.choices, default=Status.CURRENT, max_length=15, verbose_name="Статус"
    )

    def __str__(self) -> str:
        return self.name if self.name else str(self.id)

    class Meta:
        managed = False
        db_table = 'projects_project'
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

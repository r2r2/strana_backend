from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    Жилой комплекс
    """
    class Status(models.TextChoices):
        """
        Поля для статусов
        """
        CURRENT = "current", _("Текущий")
        COMPLETED = "completed", _("Завершённый")
        FUTURE = "future", _("Будущий")

    global_id = models.CharField(
        unique=True,
        max_length=200,
        blank=True,
        null=True,
        help_text="По данному ID производится синхронизация с Порталом",
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey('references.Cities', models.SET_NULL, blank=True, null=True)
    amocrm_enum = models.BigIntegerField(
        help_text="ID проекта в АМО. Необходим для синхронизации с АМО. Задается на портале и импортируется в ЛК",
        blank=True,
        null=True,
    )
    amocrm_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Название проекта в АМО. Необходимо для синхронизации с АМО. "
                  "Задается на портале и импортируется в ЛК",
    )
    amocrm_organization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Организация, закрепленная за проектом в АМО (если есть). "
                  "Необходимо для синхронизации с АМО. Задается на портале и импортируется в ЛК",
    )
    amo_responsible_user_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="ID пользователя АМО, который станет ответственным по умолчанию за создаваемые в АМО сделки. "
                  "Необходимо для синхронизации с АМО. Задается на портале и импортируется в ЛК",
    )
    amo_pipeline_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="ID воронки сделок в АМО. Необходимо для синхронизации с АМО. "
                  "Задается на портале и импортируется в ЛК",
    )
    slug = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField()
    priority = models.IntegerField(help_text="Чем ниже приоритет, тем раньше в списке будет выводиться ЖК")
    status = models.CharField(
        choices=Status.choices,
        default=Status.CURRENT,
        max_length=15,
        verbose_name="Статус",
        help_text="Импортируется с Портала. "
                  "Создавать договора и бронировать квартиры можно только в ЖК в статусе “Текущий”",
    )
    discount = models.PositiveSmallIntegerField(default=0, verbose_name="Скидка (%)")
    show_in_paid_booking: bool = models.BooleanField(verbose_name="Отображать в платном бронировании", default=True)

    def __str__(self) -> str:
        return self.name if self.name else str(self.id)

    class Meta:
        managed = False
        db_table = 'projects_project'
        verbose_name = "Жилой комплекс"
        verbose_name_plural = "3.4. [Справочник] Жилые комплексы"

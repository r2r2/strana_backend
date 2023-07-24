from django.db import models
from django.utils.translation import gettext_lazy as _


class Property(models.Model):
    """
    Объект недвижимости
    """

    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    article = models.CharField(max_length=50, blank=True, null=True)
    plan = models.ImageField(max_length=300, blank=True, null=True, upload_to="p/p/p")
    plan_png = models.ImageField(max_length=300, blank=True, null=True, upload_to="p/p/pp")
    price = models.BigIntegerField(blank=True, null=True)
    original_price = models.BigIntegerField(blank=True, null=True)
    final_price = models.BigIntegerField(blank=True, null=True)
    area = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    deadline = models.CharField(max_length=50, blank=True, null=True)
    discount = models.BigIntegerField(blank=True, null=True)
    project = models.ForeignKey("properties.Project", models.CASCADE, blank=True, null=True)
    floor = models.ForeignKey("properties.Floor", models.CASCADE, blank=True, null=True)
    building = models.ForeignKey("properties.Building", models.CASCADE, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    rooms = models.SmallIntegerField(blank=True, null=True)
    premise = models.CharField(max_length=30, blank=True, null=True)
    total_floors = models.SmallIntegerField(blank=True, null=True)
    special_offers = models.TextField(null=True, blank=True)
    similar_property_global_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        project_name = self.project.name if self.project else "-"
        propety = str(self.article) if self.article else str(self.id)  # pylint: disable=no-member
        return f"{propety}, ЖК {project_name}, {self.rooms}-ком, " \
            f"{self.area} м2, {self.floor}-эт, {self.number} ном"

    class Meta:
        managed = False
        db_table = "properties_property"
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "3.1. Объекты недвижимости"


class Building(models.Model):
    """
    Корпус
    """

    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Название")
    built_year = models.IntegerField(blank=True, null=True, verbose_name="Год сдачи")
    ready_quarter = models.IntegerField(blank=True, null=True)
    booking_active = models.BooleanField()
    project = models.ForeignKey("properties.Project", models.CASCADE, blank=True, null=True, verbose_name="Проект (ЖК)")
    total_floor = models.IntegerField(blank=True, null=True, verbose_name="Всего этажей")
    default_commission = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Комиссия по умолчания (%)"
    )
    flats_reserv_time = models.FloatField(
        verbose_name="Время бронирования квартиры",
        help_text="Определяет время бесплатного резервирования квартиры для агента",
        null=True,
        blank=True,
    )
    discount = models.PositiveSmallIntegerField(default=0, verbose_name="Скидка (%)")

    def __str__(self) -> str:
        project_name = self.project.name if self.project else "-"
        name = self.name if self.name else self.id
        return f"[{project_name}] {name}"

    class Meta:
        managed = False
        db_table = "buildings_building"
        verbose_name = "Корпус"
        verbose_name_plural = "3.2. [Справочник] Корпуса"


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
        help_text="По данному ID производится синхронизация с Порталом. "
                  "Amocrm enum - ID проекта в АМО. Необходим для синхронизации с АМО. "
                  "Задается на портале и импортируется в ЛК",
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey('references.Cities', models.SET_NULL, blank=True, null=True)
    amocrm_enum = models.BigIntegerField(blank=True, null=True)
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
    flats_reserv_time = models.FloatField(
        verbose_name="Время бронирования квартиры",
        help_text="Устанавливается в том случае, если не задано время резервирования для конкретного корпуса. "
                  "Определяет время бесплатного резервирования квартиры для агента",
        null=True,
        blank=True,
    )
    discount = models.PositiveSmallIntegerField(default=0, verbose_name="Скидка (%)")

    def __str__(self) -> str:
        return self.name if self.name else str(self.id)

    class Meta:
        managed = False
        db_table = 'projects_project'
        verbose_name = "Жилой комплекс"
        verbose_name_plural = "3.3. [Справочник] Жилые комплексы"


class Floor(models.Model):
    """
    Этаж
    """
    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    building = models.ForeignKey("properties.Building", models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        number = self.number if self.number else str(self.id)
        building_name = self.building.name if self.building else "-"
        project_name = self.building.project.name if (building_name and self.building.project) else "-"
        return f"[{project_name} -> {building_name}] {number}"

    class Meta:
        managed = False
        db_table = 'floors_floor'
        verbose_name = "Этаж"
        verbose_name_plural = "3.4. [Справочник] Этажи"

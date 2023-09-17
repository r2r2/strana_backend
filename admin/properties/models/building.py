from django.db import models


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
    discount = models.PositiveSmallIntegerField(default=0, verbose_name="Скидка (%)")
    show_in_paid_booking: bool = models.BooleanField(verbose_name="Отображать в платном бронировании", default=True)

    def __str__(self) -> str:
        project_name = self.project.name if self.project else "-"
        name = self.name if self.name else self.id
        return f"[{project_name}] {name}"

    class Meta:
        managed = False
        db_table = "buildings_building"
        verbose_name = "Корпус"
        verbose_name_plural = "3.2. [Справочник] Корпуса"

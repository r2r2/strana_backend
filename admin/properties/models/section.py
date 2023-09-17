from django.db import models


class Section(models.Model):
    """
    Секция
    """

    name = models.CharField(max_length=50, blank=True, verbose_name="Название")
    building = models.ForeignKey(
        "properties.Building", models.CASCADE, blank=True, null=True, verbose_name="Корпус"
    )
    total_floors = models.IntegerField(blank=True, null=True, verbose_name="Всего этажей")
    number = models.CharField(max_length=50, blank=True, verbose_name="Номер")

    def __str__(self) -> str:
        if self.building:
            building_name = self.building.name
            project_name = self.building.project.name if self.building.project else "-"
        else:
            building_name = project_name = "-"
        name = self.name if self.name else self.id
        return f"[{project_name} -> {building_name}] {name}"

    class Meta:
        managed = False
        db_table = "buildings_section"
        verbose_name = "Секция"
        verbose_name_plural = "3.3. [Справочник] Секции"

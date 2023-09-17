from django.db import models


class Floor(models.Model):
    """
    Этаж
    """
    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер этажа")
    building = models.ForeignKey("properties.Building", models.CASCADE, blank=True, null=True, verbose_name="Корпус")

    def __str__(self) -> str:
        number = self.number if self.number else str(self.id)
        building_name = self.building.name if self.building else "-"
        project_name = self.building.project.name if (building_name and self.building.project) else "-"
        return f"[{project_name} -> {building_name}] {number}"

    class Meta:
        managed = False
        db_table = 'floors_floor'
        verbose_name = "Этаж"
        verbose_name_plural = "3.5. [Справочник] Этажи"

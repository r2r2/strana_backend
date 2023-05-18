from django.db import models


class Building(models.Model):
    """
    Корпус
    """

    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    built_year = models.IntegerField(blank=True, null=True)
    ready_quarter = models.IntegerField(blank=True, null=True)
    booking_active = models.BooleanField()
    project = models.ForeignKey("projects.Project", models.CASCADE, blank=True, null=True)
    total_floor = models.IntegerField(blank=True, null=True)
    default_commission = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self) -> str:
        return self.name if self.name else str(self.id)

    class Meta:
        managed = False
        db_table = "buildings_building"
        verbose_name = "Корпус"
        verbose_name_plural = "Корпуса"

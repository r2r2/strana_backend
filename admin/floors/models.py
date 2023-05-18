from django.db import models


class Floor(models.Model):
    """
    Этаж
    """
    global_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    building = models.ForeignKey("buildings.Building", models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return self.number if self.number else str(self.id)

    class Meta:
        managed = False
        db_table = 'floors_floor'
        verbose_name = "Этаж"
        verbose_name_plural = "Этажи"

from django.db import models


class Cities(models.Model):
    """
    Города
    """
    name = models.CharField(verbose_name="Название", max_length=150)
    slug = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "cities_city"
        verbose_name = "Город"
        verbose_name_plural = "Города"



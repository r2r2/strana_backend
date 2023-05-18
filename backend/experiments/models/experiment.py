from django.db import models


class Experiment(models.Model):
    tag = models.CharField(verbose_name="Тэг", max_length=200, unique=True)
    name = models.CharField(verbose_name="Название эксперемента", max_length=200)
    is_active = models.BooleanField(verbose_name="Активный", default=False)

    class Meta:
        verbose_name = "Эксперементы"
        verbose_name_plural = "Эксперементы"

    def __str__(self):
        return f'{self.name}'

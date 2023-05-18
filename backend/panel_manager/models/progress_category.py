from django.db import models


class ProgressCategory(models.Model):

    progress = models.ForeignKey(
        verbose_name="Ход строительства", to="panel_manager.Progress", on_delete=models.CASCADE
    )
    name = models.CharField("Наименование", max_length=200)

    class Meta:
        verbose_name = "Категория хода строительства"
        verbose_name_plural = "Категория хода строительства"

    def __str__(self):
        return self.name

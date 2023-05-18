from django.db import models


class Tip(models.Model):
    """
    Подсказка
    """

    image = models.ImageField(max_length=500, blank=True, null=True, upload_to="t/t/i")
    title = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tips_tip"
        verbose_name = "Подсказка"
        verbose_name_plural = "Подсказки"
        ordering = ("order",)

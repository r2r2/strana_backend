from django.db import models


class BaseBlock(models.Model):
    """ Базовая модель блока """

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)
    landing = models.ForeignKey("landing.Landing", verbose_name="Лендинг", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self._meta.verbose_name} №{self.order + 1}"

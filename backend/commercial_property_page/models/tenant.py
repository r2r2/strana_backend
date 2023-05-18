from django.db import models
from ajaximage.fields import AjaxImageField


class Tenant(models.Model):
    """
    Арендатор
    """

    name = models.CharField(verbose_name="Название", max_length=200)
    logo = AjaxImageField(verbose_name="Логотип", upload_to="t/image", blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)
    cities = models.ManyToManyField('cities.City', verbose_name='Города', blank=True)

    def __str__(self) -> str:
        return f'{self._meta.verbose_name} "{self.name}"'

    class Meta:
        verbose_name = "Арендатор"
        verbose_name_plural = "Арендаторы"
        ordering = ("order",)

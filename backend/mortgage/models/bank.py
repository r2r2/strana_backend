from django.db import models
from ajaximage.fields import AjaxImageField
from ..queryset import BankQuerySet


class Bank(models.Model):
    """
    Банк
    """

    objects = BankQuerySet.as_manager()

    name = models.CharField(verbose_name="Название банка", max_length=100)
    logo = AjaxImageField(verbose_name="Логотип", upload_to="bank/logo")
    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)
    dvizh_id = models.PositiveIntegerField(verbose_name="id банка в Движ.API", null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Банк"
        verbose_name_plural = "Банки"
        ordering = ("order",)

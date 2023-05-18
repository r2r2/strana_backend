from django.db import models
from ckeditor.fields import RichTextField


class VacancyCategory(models.Model):
    """
    Категория вакансии
    """

    name = models.CharField(verbose_name='Название категории', max_length=200)
    img = models.ImageField(
        verbose_name='Иконка', upload_to="f/ip", null=True, blank=True
    )
    desc = RichTextField(verbose_name='Текст при наведении на карточку', null=True, blank=True)

    order = models.PositiveIntegerField(verbose_name="Очередность", default=0)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Категория вакансии"
        verbose_name_plural = "Категории вакансий"
        ordering = ("order",)

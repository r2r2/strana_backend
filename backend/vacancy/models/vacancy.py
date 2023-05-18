from ckeditor.fields import RichTextField
from django.db import models
from ..constants import WorkFormat


class Vacancy(models.Model):
    """
    Вакансия
    """

    job_title = models.CharField(verbose_name="Должность", max_length=200)
    announcement = RichTextField(verbose_name="Анонс", blank=True)
    duties = RichTextField(verbose_name="Обязанности", blank=True)
    requirements = RichTextField(verbose_name="Требования", blank=True)
    conditions = RichTextField(verbose_name="Условия ", blank=True)
    date = models.DateField(verbose_name="Дата добавления", null=True, blank=True)
    order = models.PositiveIntegerField(verbose_name="Очередность", default=0, db_index=True)
    is_active = models.BooleanField(verbose_name="Активно", default=True)
    work_format = models.ForeignKey(
        verbose_name="Формат работы",
        to="vacancy.VacancyFormat",
        on_delete=models.SET_NULL,
        null=True
    )
    city = models.ManyToManyField(to="cities.City", blank=True, verbose_name='Города', related_name='city')
    category = models.ForeignKey(
        verbose_name="Категория", to="vacancy.VacancyCategory", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.job_title

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ("order",)

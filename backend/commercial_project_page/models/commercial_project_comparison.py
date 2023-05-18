from django.db import models


class CommercialProjectComparison(models.Model):
    """ Модель сравнения коммерческого проекта """

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)
    commercial_project_page = models.OneToOneField(
        verbose_name="Страница коммерческого проекта",
        to="commercial_project_page.CommercialProjectPage",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Сравнение коммерческого проекта"
        verbose_name_plural = "Сравнения коммерческих проектов"

    def __str__(self) -> str:
        return self.title


class CommercialProjectComparisonItem(models.Model):
    """ Модель элемента сравнения коммерческого проекта """

    name = models.CharField(verbose_name="Название", max_length=128)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)
    comparison = models.ForeignKey(
        verbose_name="Сравнение",
        to=CommercialProjectComparison,
        on_delete=models.CASCADE,
        related_name="items",
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Элемент сравнения коммерческого проекта"
        verbose_name_plural = "Элемент сравнения коммерческого проекта"

    def __str__(self) -> str:
        return self.title

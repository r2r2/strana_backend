from django.db import models

from common.models import Spec, MultiImageMeta


class CommercialInvestCard(models.Model, metaclass=MultiImageMeta):
    """ Модель карточки инвестиции в коммерческий проект """

    WIDTH = 400
    HEIGHT = 600

    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=200, blank=True)
    image = models.ImageField(
        verbose_name="Изображение", upload_to="cpp/cic/i", null=True, blank=True
    )
    commercial_project_page = models.ForeignKey(
        verbose_name="Страница коммерческого проекта",
        to="commercial_project_page.CommercialProjectPage",
        on_delete=models.CASCADE,
    )

    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Карточка инвестиций"
        verbose_name_plural = "Карточки инвестиций"

    def __str__(self) -> str:
        return self.title

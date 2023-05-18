from ckeditor.fields import RichTextField
from django.db import models
from solo.models import SingletonModel

from common.models import Spec, MultiImageMeta



class MallTeam(SingletonModel):
    title = RichTextField("Заголовок блока")

    class Meta:
        verbose_name = verbose_name_plural = "Блок 'MALLTEAM'"

    def __str__(self):
        return self.title


class MallTeamAdvantage(models.Model, metaclass=MultiImageMeta):
    WIDTH = 400
    HEIGHT = 600

    order = models.PositiveIntegerField("Порядок", default=0)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=200, blank=True)
    image = models.ImageField(
        verbose_name="Изображение", upload_to="cpp/mt/i", null=True, blank=True
    )
    mall_team_block = models.ForeignKey(
        verbose_name="Блок",
        to=MallTeam,
        on_delete=models.CASCADE,
    )

    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Карточка Преимущества MallTeam"
        verbose_name_plural = "Карточки Преимуществ MallTeam"

    def __str__(self) -> str:
        return self.title

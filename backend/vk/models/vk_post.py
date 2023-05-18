from datetime import datetime
from ckeditor.fields import RichTextField
from django.db import models
from common.models import MultiImageMeta, Spec


class VkPost(models.Model, metaclass=MultiImageMeta):
    """
    Пост в vk
    """

    IMAGE_WIDTH = 840
    IMAGE_HEIGHT = 720

    link = models.URLField(verbose_name="Ссылка", max_length=200, null=True, blank=True)
    descriptions = RichTextField(verbose_name="Описание поста", blank=True)
    shortcode = models.CharField(verbose_name="Код поста", max_length=200, db_index=True)
    likes = models.PositiveIntegerField(verbose_name="Количество лайков", default=0)
    timestamp = models.PositiveIntegerField(verbose_name="Таймстап поста", default=0)
    published = models.BooleanField(verbose_name="Опубликовать пост на сайте", default=False)

    image = models.ImageField(
        verbose_name="Изображение", upload_to="vk/image", help_text="На обложке", blank=True
    )

    account = models.ForeignKey(
        verbose_name="Аккаунт",
        to="vk.VkAccount",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"Пост от {datetime.fromtimestamp(self.timestamp)}"

    class Meta:
        verbose_name = "Пост в vk"
        verbose_name_plural = "Посты в vk"
        ordering = ("-timestamp",)

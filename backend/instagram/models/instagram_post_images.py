from django.db import models
from common.models import MultiImageMeta, Spec


class InstagramPostImages(models.Model, metaclass=MultiImageMeta):
    """
    Слайд поста
    """

    IMAGE_WIDTH = 840
    IMAGE_HEIGHT = 720

    id_instagram = models.CharField(verbose_name="ID инстаграмма", max_length=200, db_index=True)
    image = models.ImageField(verbose_name="Слайд поста", upload_to="instagram/s_image")

    post = models.ForeignKey(
        verbose_name="Пост", to="instagram.InstagramPost", on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(verbose_name="Очередность", default=0)

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    class Meta:
        verbose_name = "Слайд поста"
        verbose_name_plural = "Слайды поста"
        ordering = ("order",)

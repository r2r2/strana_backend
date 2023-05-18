from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.db import models

from common.models import Spec, MultiImageMeta
from ..constants import PersonCategory


class Person(models.Model, metaclass=MultiImageMeta):
    """
    Персона
    """

    IMAGE_WIDTH = 364
    IMAGE_HEIGHT = 467

    first_name = models.CharField(verbose_name="Имя", max_length=200)
    last_name = models.CharField(verbose_name="Фамилия", max_length=200)
    patronymic = models.CharField(verbose_name="Отчество", max_length=200, blank=True)
    position = models.CharField(verbose_name="Должность", max_length=200)
    category = models.CharField(
        "Категория", choices=PersonCategory.choices, blank=True, max_length=32
    )
    bio = RichTextField("Биография", blank=True)

    image = AjaxImageField(
        verbose_name="Фотография",
        upload_to="person/image",
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    image_hover = AjaxImageField(
        verbose_name="Фотография при ховере",
        blank=True,
        upload_to="person/image_hover",
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    image_popup = AjaxImageField(
        verbose_name="Фотография в модальном окне",
        blank=True,
        upload_to="person/image_popup",
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )

    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_hover_display": Spec("image_hover", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_hover_preview": Spec("image_hover", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_popup_display": Spec("image_popup", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_popup_preview": Spec("image_popup", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    class Meta:
        verbose_name = "Персона"
        verbose_name_plural = "Персоны"
        ordering = ("order",)

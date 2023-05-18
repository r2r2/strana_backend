from ajaximage.fields import AjaxImageField
from django.db import models
from common.models import MultiImageMeta, Spec


class FlatRoomsMenu(models.Model, metaclass=MultiImageMeta):
    """
    Изображение квартиры для меню
    """

    IMAGE_WIDTH = 830
    IMAGE_HEIGHT = 942

    rooms_0_text = models.CharField(verbose_name="Студии / Текст", blank=True, max_length=200)
    rooms_1_text = models.CharField(verbose_name="1-комнатные / Текст", blank=True, max_length=200)
    rooms_2_text = models.CharField(verbose_name="2-комнатные / Текст", blank=True, max_length=200)
    rooms_3_text = models.CharField(verbose_name="3-комнатные / Текст", blank=True, max_length=200)
    rooms_4_text = models.CharField(verbose_name="4-комнатные / Текст", blank=True, max_length=200)

    rooms_0_image = AjaxImageField(
        verbose_name="Студии / Изображение",
        upload_to="p/m/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    rooms_1_image = AjaxImageField(
        verbose_name="1-комнатные / Изображение",
        upload_to="p/m/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    rooms_2_image = AjaxImageField(
        verbose_name="2-комнатные / Изображение",
        upload_to="p/m/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    rooms_3_image = AjaxImageField(
        verbose_name="3-комнатные / Изображение",
        upload_to="p/m/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    rooms_4_image = AjaxImageField(
        verbose_name="4-комнатные / Изображение",
        upload_to="p/m/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )

    city = models.OneToOneField(
        verbose_name="Город",
        to="cities.City",
        on_delete=models.CASCADE,
        related_name="flat_rooms_menu",
    )

    image_map = {
        "rooms_zero_image_display": Spec("rooms_0_image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "rooms_zero_image_preview": Spec("rooms_0_image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "rooms_one_image_display": Spec("rooms_1_image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "rooms_one_image_preview": Spec("rooms_1_image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "rooms_two_image_display": Spec("rooms_2_image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "rooms_two_image_preview": Spec("rooms_2_image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "rooms_three_image_display": Spec("rooms_3_image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "rooms_three_image_preview": Spec("rooms_3_image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "rooms_four_image_display": Spec("rooms_4_image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "rooms_four_image_preview": Spec("rooms_4_image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"{self.city} - {self._meta.verbose_name}"

    class Meta:
        verbose_name = "Изображения квартир для меню"
        verbose_name_plural = "Изображения квартир для меню"

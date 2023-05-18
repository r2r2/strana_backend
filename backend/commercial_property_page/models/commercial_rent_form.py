from django.db import models

from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField

from common.models import MultiImageMeta, Spec


class CommercialRentForm(models.Model, metaclass=MultiImageMeta):
    """
    Форма на странице коммерции
    """

    IMAGE_WIDTH = 500
    IMAGE_HEIGHT = 440
    IMAGE_PHONE_WIDTH = 56
    IMAGE_PHONE_HEIGHT = 56

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    success = models.CharField(
        verbose_name="Сообщение при успешной отправке", max_length=200, blank=True
    )
    button_text = models.CharField(verbose_name="Текст на кнопке", max_length=200, blank=True)
    full_name = models.CharField(verbose_name="ФИО", max_length=200, blank=True)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    yandex_metrics = models.CharField(
        verbose_name="Яндекс метрика", max_length=100, null=True, blank=True
    )
    google_event_name = models.CharField("Название ивента Google", max_length=100, blank=True)

    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="f/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    image_phone = models.ImageField(
        verbose_name="Изображение телефон", upload_to="f/ip", null=True, blank=True
    )

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_phone_display": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, False),
        "image_phone_preview": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"{self.id} - {self.full_name}"

    class Meta:
        verbose_name = "Форма на странице коммерции"
        verbose_name_plural = "Формы на странице коммерции"


class CommercialRentFormEmployee(models.Model, metaclass=MultiImageMeta):
    """ Сотрудник формы страницы коммерции """

    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 906
    IMAGE_PHONE_WIDTH = 112
    IMAGE_PHONE_HEIGHT = 112

    city = models.ForeignKey("cities.City", verbose_name="Город", on_delete=models.CASCADE)
    form = models.ForeignKey(
        "commercial_property_page.CommercialRentForm",
        verbose_name="Форма",
        on_delete=models.PROTECT,
    )
    full_name = models.CharField(verbose_name="ФИО", max_length=200)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="f/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    image_phone = models.ImageField(
        verbose_name="Мобильное изображение", upload_to="f/ip", null=True, blank=True
    )

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_phone_display": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, False),
        "image_phone_preview": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, True),
    }

    class Meta:
        verbose_name = "Сотрудник формы страницы коммерции"
        verbose_name_plural = "Сотрудники формы страницы коммерции"

    def __str__(self):
        return self.full_name

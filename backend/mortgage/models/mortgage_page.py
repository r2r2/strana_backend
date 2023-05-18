from django.db import models
from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.contrib.sites.models import Site
from common.models import MultiImageMeta, Spec


class MortgagePage(models.Model):
    """
    Страница ипотеки
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    formattable_title = models.CharField(
        verbose_name="Заголовок с форматированием", max_length=200, blank=True
    )
    min_value = models.FloatField(verbose_name="Мин ставка", null=True, blank=True)
    button_text_1 = models.CharField(verbose_name="Текст кнопки 1", max_length=100, blank=True)
    button_link_1 = models.URLField(verbose_name="Ссылка на кнопке 1", blank=True)
    button_text_2 = models.CharField(verbose_name="Текст кнопки 2", max_length=100, blank=True)
    button_link_2 = models.URLField(verbose_name="Ссылка на кнопке 2", blank=True)

    site = models.ForeignKey(
        verbose_name="Сайт", to=Site, on_delete=models.CASCADE, blank=True, null=True
    )
    form = models.ForeignKey(
        verbose_name="Форма",
        to="mortgage.MortgagePageForm",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} {self.site.name}"

    class Meta:
        verbose_name = "Страница ипотеки"
        verbose_name_plural = "Страницы ипотеки"


class MortgageAdvantage(models.Model):
    """
    Преимущество ипотеки
    """

    title = models.CharField(verbose_name="Заголовок", max_length=100)
    formattable_title = models.CharField(
        verbose_name="Заголовок с форматированием", max_length=200, blank=True
    )
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    min_value = models.FloatField(verbose_name="Мин ставка", null=True, blank=True)
    page = models.ForeignKey(
        verbose_name="Страница ипотеки",
        to=MortgagePage,
        on_delete=models.CASCADE,
        related_name="advantages",
    )

    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} {self.id}"

    class Meta:
        verbose_name = "Преимущество ипотеки"
        verbose_name_plural = "Преимущества ипотеки"
        ordering = ("order",)


class MortgageInstrument(models.Model, metaclass=MultiImageMeta):
    """
    Ипотечный инструмент
    """

    WIDTH = 486
    HEIGHT = 464

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = models.TextField(verbose_name="Описание", blank=True)

    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="mortgage/instruments",
        null=True,
        blank=True,
        help_text=f"шир. - {WIDTH}, выс. - {HEIGHT}",
    )

    page = models.ForeignKey(
        verbose_name="Страница ипотеки",
        to=MortgagePage,
        on_delete=models.CASCADE,
        related_name="instruments",
    )

    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} {self.id}"

    class Meta:
        verbose_name = "Карточка ипотечных инструментов"
        verbose_name_plural = "Карточки ипотечных инструментов"
        ordering = ("order",)


class MortgagePageForm(models.Model, metaclass=MultiImageMeta):
    """
    Форма на странице ипотеки
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
        verbose_name = "Форма на странице ипотеки"
        verbose_name_plural = "Формы на странице ипотеки"


class MortgagePageFormEmployee(models.Model, metaclass=MultiImageMeta):
    """ Сотрудник формы страницы ипотеки """

    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 906
    IMAGE_PHONE_WIDTH = 112
    IMAGE_PHONE_HEIGHT = 112

    city = models.ForeignKey("cities.City", verbose_name="Город", on_delete=models.CASCADE)
    form = models.ForeignKey(
        "mortgage.MortgagePageForm", verbose_name="Форма", on_delete=models.PROTECT
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
        verbose_name = "Сотрудник формы страницы ипотеки"
        verbose_name_plural = "Сотрудники формы страницы ипотеки"

    def __str__(self):
        return self.full_name

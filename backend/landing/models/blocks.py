from ckeditor.fields import RichTextField
from django.db import models

from news.constants import NewsType
from common.models import Spec, OrderedImage, MultiImageMeta
from properties.constants import PropertyType, PropertyStatus
from ..constants import CTABlockType, LandingBlockChoices
from .abstract import BaseBlock


class LandingBlock(BaseBlock, metaclass=MultiImageMeta):
    """Модель блока лендинга"""

    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080

    title = models.CharField("Заголовок", max_length=128, blank=True)
    block_type = models.CharField("Тип блока", choices=LandingBlockChoices.choices, max_length=64)
    anchor = models.CharField("Якорь блока", blank=True, max_length=32)
    text = RichTextField("Текст", blank=True)

    image_1 = models.ImageField("Изображение", upload_to="lnd/lb/i", blank=True)
    image_1_description = models.TextField("Описание изображения", blank=True)
    image_2 = models.ImageField("Изображение (2)", upload_to="lnd/lb/i2", blank=True)
    image_2_description = models.TextField("Описание изображения (2)", blank=True)
    image_3 = models.ImageField("Изображение (3)", upload_to="lnd/lb/i3", blank=True)
    is_full_screen = models.BooleanField(
        "Full-screen слайды",
        default=False,
        help_text="Для блока со слайдером. В полноэкранном режиме не отображается текст",
    )

    cta_block_type = models.CharField(
        "Тип CTA блока",
        choices=CTABlockType.choices,
        max_length=20,
        help_text="для CTA блока",
        default=CTABlockType.PRESENTATION,
    )
    presentation = models.FileField(
        "Презентация",
        blank=True,
        upload_to="lnd/cta/f",
        help_text="для CTA блока, будет отправлена на почту",
    )
    send_to_email = models.BooleanField(
        "Отправлять презентацию на почту",
        default=False,
        help_text="Если включен, появится форма с email, иначе будет отображаться кнопка 'Скачать'",
    )

    button_name_1 = models.CharField("Надпись на кнопке (1)", blank=True, max_length=64)
    button_link_1 = models.CharField("Ссылка на кнопке (1)", blank=True, max_length=258)
    button_name_2 = models.CharField("Надпись на кнопке (2)", blank=True, max_length=64)
    button_link_2 = models.CharField("Ссылка на кнопке (2)", blank=True, max_length=258)

    text_end = models.TextField("Текст в конце блока", blank=True)

    project = models.ForeignKey(
        to="projects.Project",
        verbose_name="Проект",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Для блока квартир и прогресс",
    )

    flat_set = models.ManyToManyField(
        to="properties.Property",
        verbose_name="Квартиры",
        blank=True,
        limit_choices_to={"type": PropertyType.FLAT, "status": PropertyStatus.FREE},
        help_text="Для блока квартир",
    )

    furnishes = models.ManyToManyField(
        verbose_name="Варианты отделки",
        to="properties.Furnish",
        blank=True,
        help_text="Для блока с отделкой",
    )
    progress_set = models.ManyToManyField(
        verbose_name="Новости ход строительства",
        to="news.News",
        limit_choices_to={"type": NewsType.PROGRESS},
        blank=True,
        related_name="+",
        help_text="Для блока прогресс",
    )

    news_set = models.ManyToManyField(
        verbose_name="Новости",
        to="news.News",
        blank=True,
        related_name="+",
        help_text="Для блока новости",
    )

    image_map = {
        "image1_display": Spec("image_1", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image1_preview": Spec("image_1", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image2_display": Spec("image_2", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image2_preview": Spec("image_2", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image3_display": Spec("image_3", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image3_preview": Spec("image_3", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Блок лендинга"
        verbose_name_plural = "Блоки лендинга"

    def __str__(self):
        return f"{self.get_block_type_display()} #{self.order + 1}"


class SliderBlockSlide(OrderedImage):
    """Модель слайда блока слайдера"""

    WIDTH = 3200
    HEIGHT = 1900
    upload_to = "lnd/sbs/i"

    block = models.ForeignKey(LandingBlock, on_delete=models.CASCADE, related_name="slides")

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Слайд блока со слайдером"
        verbose_name_plural = "Слайды блока со слайдером"

    def __str__(self):
        return f"Слайд {self.order + 1}"


class TwoColumnsBlockItem(OrderedImage):
    WIDTH = 500
    HEIGHT = 240
    upload_to = "lnd/tc/i"

    subtitle = models.CharField("Подзаголовок изображения", blank=True, max_length=256)
    description = models.TextField("Описание изображения", blank=True)
    block = models.ForeignKey(
        LandingBlock, verbose_name="Блок", on_delete=models.CASCADE, related_name="two_column_items"
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Элемент блока c иконками в две колонки"
        verbose_name_plural = "Элементы блока c иконками в две колонки"


class DigitsBlockItem(models.Model):
    """Элемент блока цифры"""

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    title = models.CharField("Заголовок", max_length=128)
    subtitle = models.CharField("Подзаголовок", max_length=128, blank=True)
    text = models.TextField("Текст", blank=True)
    block = models.ForeignKey(
        LandingBlock, verbose_name="Блок", on_delete=models.CASCADE, related_name="digit_items"
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Элемент блока цифры"
        verbose_name_plural = "Элемент блока цифры"


class AdvantageBlockItem(OrderedImage):
    WIDTH = 840
    HEIGHT = 720
    upload_to = "lnd/adv/i"

    subtitle = models.CharField("Подзаголовок изображения", blank=True, max_length=256)
    description = models.TextField("Описание изображения", blank=True)
    block = models.ForeignKey(
        LandingBlock, verbose_name="Блок", on_delete=models.CASCADE, related_name="advantages"
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Элемент блока преимуществ"
        verbose_name_plural = "Элементы блока преимуществ"


class StepsBlockItem(models.Model):
    """Элемент Блока шаги"""

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    title = models.CharField("Заголовок", max_length=128)
    text = models.TextField("Текст", blank=True)
    block = models.ForeignKey(
        LandingBlock, verbose_name="Блок", on_delete=models.CASCADE, related_name="steps"
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Элемент блока шаги"
        verbose_name_plural = "Элемент блока шаги"


class ListBlockItem(models.Model):
    """Элемент блока со списокм"""

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    title = models.CharField("Заголовок", max_length=128)
    block = models.ForeignKey(
        LandingBlock, verbose_name="Блок", on_delete=models.CASCADE, related_name="list_items"
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Элемент блока со списокм"
        verbose_name_plural = "Элементы блока со списокм"

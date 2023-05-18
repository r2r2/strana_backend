from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.contrib.sites.models import Site
from django.db import models
from common.models import OrderedImage, Spec, MultiImageMeta
from .querysets import MainPageSlideQuerySet

from projects.models import Project


class MainPage(models.Model):
    """
    Главная страница
    """

    site = models.ForeignKey(
        verbose_name="Сайт", to=Site, on_delete=models.CASCADE, blank=True, null=True
    )

    news_title = models.CharField(verbose_name="Новости / Заголовок", max_length=200, blank=True)
    news_image = AjaxImageField(verbose_name="Изображение", null=True, blank=True)

    side_block_title_1 = models.CharField(
        verbose_name="Боковой блок 1 / Заголовок", max_length=200, blank=True
    )
    side_block_text_1 = RichTextField(verbose_name="Боковой блок 1 / Текст", blank=True)
    side_block_image_1 = AjaxImageField(
        verbose_name="Боковой блок 1 / Изображение", null=True, blank=True
    )
    side_block_hover_text_1 = RichTextField(
        verbose_name="Боковой блок 1 / Текст при ховере", blank=True
    )
    side_block_link_1 = models.URLField(
        verbose_name="Боковой блок 1 / Ссылка", null=True, blank=True
    )

    side_block_title_2 = models.CharField(
        verbose_name="Боковой блок 2 / Заголовок", max_length=200, blank=True
    )
    side_block_title_2_mobile = models.CharField(
        verbose_name="Боковой блок 2 мообильный / Заголовок", max_length=200, blank=True
    )

    side_block_text_2 = RichTextField(verbose_name="Боковой блок 2 / Текст", blank=True)
    side_block_image_2 = AjaxImageField(
        verbose_name="Боковой блок 2 / Изображение", null=True, blank=True
    )
    side_block_hover_text_2 = RichTextField(
        verbose_name="Боковой блок 2 / Текст при ховере", blank=True
    )
    side_block_link_2 = models.URLField(
        verbose_name="Боковой блок 2 / Ссылка", null=True, blank=True
    )

    ideology_text_1 = RichTextField(verbose_name="Идеология / Текст 1", blank=True)
    ideology_text_2 = RichTextField(verbose_name="Идеология / Текст 2", blank=True)
    ideology_image_1 = AjaxImageField(
        verbose_name="Идеология / Изображение 1", null=True, blank=True
    )
    ideology_image_2 = AjaxImageField(
        verbose_name="Идеология / Изображение 1", null=True, blank=True
    )
    ideology_video_link_1 = models.URLField(
        verbose_name="Идеология / Ссылка на видео 1", blank=True
    )
    ideology_video_preview_1 = AjaxImageField(
        verbose_name="Идеология / Превью видео 1", null=True, blank=True
    )
    ideology_video_link_2 = models.URLField(
        verbose_name="Идеология / Ссылка на видео 2", blank=True
    )
    ideology_video_preview_2 = AjaxImageField(
        verbose_name="Идеология / Превью видео 2", null=True, blank=True
    )
    ideology_button_text = models.CharField(
        verbose_name="Идеология / Текст кнопки", max_length=100, blank=True
    )
    ideology_button_link = models.URLField(verbose_name="Идеология / Ссылка на кнопке", blank=True)

    map_texts = models.ManyToManyField(
        verbose_name="Тексты для карты", to="main_page.MapText", blank=True
    )

    def __str__(self) -> str:
        return f"Главная страница {self.site.name}"

    class Meta:
        verbose_name = "Главная страница"
        verbose_name_plural = "Главные страницы"


class MapText(models.Model):
    """
    Текст для карты
    """

    text = models.CharField(verbose_name="Текст", max_length=400)
    red_text = models.CharField(verbose_name="Красный текст", max_length=400, blank=True)

    def __str__(self) -> str:
        return f"Текст для карты - {self.id}"

    class Meta:
        verbose_name = "Текст для карты"
        verbose_name_plural = "Тексты для карты"


class MainPageSlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд на главной
    """

    WIDTH_DESKTOP_BIG = 3200
    HEIGHT_DESKTOP_BIG = 1900
    WIDTH_DESKTOP_SMALL = 1830
    HEIGHT_DESKTOP_SMALL = 1168
    WIDTH_TABLET = 1152
    HEIGHT_TABLET = 811
    WIDTH_PHONE = 1280
    HEIGHT_PHONE = 1568

    objects = MainPageSlideQuerySet.as_manager()

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    text = RichTextField(verbose_name="Текст", blank=True)
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    end_date = models.DateTimeField(
        verbose_name="Дата окончания",
        blank=True,
        null=True,
        help_text="При наступлении даты, слайд деактивируется",
    )
    red_text = models.CharField(verbose_name="Красный текст", max_length=400, blank=True)
    form_title = models.CharField(
        verbose_name="Заголовок формы",
        max_length=64,
        blank=True,
        help_text="Если заполнен, на слайде появляется форма",
    )
    button_text = models.CharField(verbose_name="Текст кнопки", max_length=100, blank=True)
    button_project = models.OneToOneField(
        Project, on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name='Проект'
    )
    button_link = models.CharField(verbose_name="Ссылка на кнопке", blank=True, max_length=1000)
    blank = models.BooleanField(verbose_name="Открывать ссылку в новой вкладке", default=False)

    image_desktop_big = models.ImageField(
        verbose_name="Изображение десктоп (большое)", upload_to="mp/mps/idb", null=True, blank=True
    )
    image_desktop_small = models.ImageField(
        verbose_name="Изображение десктоп (маленькое)",
        upload_to="mp/mps/ids",
        null=True,
        blank=True,
    )
    image_tablet = models.ImageField(
        verbose_name="Изображение планшет", upload_to="mp/mps/it", null=True, blank=True
    )
    image_phone = models.ImageField(
        verbose_name="Изображение телефон", upload_to="mp/mps/ip", null=True, blank=True
    )
    page = models.ForeignKey(
        verbose_name="Главная страница",
        to=MainPage,
        on_delete=models.CASCADE,
        related_name="slides",
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    image_map = {
        "image_desktop_big_display": Spec(
            source="image_desktop_big", width=WIDTH_DESKTOP_BIG, height=HEIGHT_DESKTOP_BIG
        ),
        "image_desktop_big_preview": Spec(
            source="image_desktop_big",
            width=WIDTH_DESKTOP_BIG,
            height=HEIGHT_DESKTOP_BIG,
            blur=True,
        ),
        "image_desktop_small_display": Spec(
            source="image_desktop_small", width=WIDTH_DESKTOP_SMALL, height=HEIGHT_DESKTOP_SMALL
        ),
        "image_desktop_small_preview": Spec(
            source="image_desktop_small",
            width=WIDTH_DESKTOP_SMALL,
            height=HEIGHT_DESKTOP_SMALL,
            blur=True,
        ),
        "image_tablet_display": Spec(
            source="image_tablet", width=WIDTH_TABLET, height=HEIGHT_TABLET
        ),
        "image_tablet_preview": Spec(
            source="image_tablet", width=WIDTH_TABLET, height=HEIGHT_TABLET, blur=True
        ),
        "image_phone_display": Spec(source="image_phone", width=WIDTH_PHONE, height=HEIGHT_PHONE),
        "image_phone_preview": Spec(
            source="image_phone", width=WIDTH_PHONE, height=HEIGHT_PHONE, blur=True
        ),
    }

    def __str__(self) -> str:
        return f"Слайд на главной {self.id}"

    class Meta:
        verbose_name = "Слайд на главной"
        verbose_name_plural = "Слайды на главной"
        ordering = ("order",)


class MainPageIdeologyCard(OrderedImage):
    """
    Карточка идеологии на главной
    """

    upload_to = "main_page/slides"
    WIDTH = 840
    HEIGHT = 664

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    text = RichTextField(verbose_name="Текст", blank=True)

    page = models.ForeignKey(
        verbose_name="Главная страница",
        to=MainPage,
        on_delete=models.CASCADE,
        related_name="ideology_cards",
    )

    order = models.PositiveSmallIntegerField("Порядок", default=0, db_index=True)

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return f"Карточка идеологии {self.id}"

    class Meta:
        verbose_name = "Карточка идеологии на главной"
        verbose_name_plural = "Карточки идеологии на главной"
        ordering = ("order",)


class MainPageStory(OrderedImage):
    """Модель истории на главной странице"""

    upload_to = "main_page/stories"
    WIDTH = 215
    HEIGHT = 276

    name = models.CharField("Название", max_length=32)
    page = models.ForeignKey(
        verbose_name="Главная страница",
        to=MainPage,
        on_delete=models.CASCADE,
        related_name="stories",
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT, default="png"),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "История главной страницы"
        verbose_name_plural = "Истории главных страницах"

    def __str__(self):
        return self.name


class MainPageStoryImage(OrderedImage):
    """Модель изображения истории с главной страницы"""

    upload_to = "main_page/story-images"
    WIDTH = 840
    HEIGHT = 664

    text = RichTextField("Текст", blank=True)
    story = models.ForeignKey(
        MainPageStory, verbose_name="История", on_delete=models.CASCADE, related_name="images"
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Изображение истории о компании"
        verbose_name_plural = "Изображения истории о компании"

    def __str__(self) -> str:
        return str(self.order)

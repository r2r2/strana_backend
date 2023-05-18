from ckeditor.fields import RichTextField
from django.db import models
from solo.models import SingletonModel
from common.constants import FULLSCREEN_HEIGHT, FULLSCREEN_WIDTH
from common.models import MultiImageMeta, Spec, OrderedImage


class AboutPage(SingletonModel, metaclass=MultiImageMeta):
    """
    Страница о компании
    """

    text_1 = RichTextField(verbose_name="Текст 1", max_length=5000, null=True, blank=True)
    text_2 = RichTextField(verbose_name="Текст 2", max_length=5000, null=True, blank=True)

    offices = models.CharField(verbose_name="Офисы", max_length=30, null=True, blank=True)
    description = RichTextField(
        verbose_name="Описание офисов", max_length=1000, null=True, blank=True
    )

    credit_rating = models.CharField(
        verbose_name="Кредитный рейтинг", max_length=30, null=True, blank=True
    )
    credit_rating_description = RichTextField(
        verbose_name="Описание кредитного рейтинга", max_length=1000, null=True, blank=True,
    )

    image = models.ImageField(verbose_name="Изображение", upload_to="c/a/i", null=True, blank=True)
    ideology_description = RichTextField(
        verbose_name="Описание идеологии", max_length=1000, null=True, blank=True
    )
    ideology_text = RichTextField(
        verbose_name="Текст идеологии", max_length=1000, null=True, blank=True
    )
    ideology_image_one = models.ImageField(
        verbose_name="Изображение идеологии 1", upload_to="c/i/i", null=True, blank=True
    )
    ideology_image_two = models.ImageField(
        verbose_name="Изображение идеологии 2", upload_to="c/i/i", null=True, blank=True
    )
    ideology_video_one = models.URLField(verbose_name="Видео идеологии 1", null=True, blank=True)
    ideology_video_two = models.URLField(verbose_name="Видео идеологии 2", null=True, blank=True)

    map_texts = models.ManyToManyField(
        verbose_name="Тексты для карты", to="main_page.MapText", blank=True
    )

    image_map = {
        "image_display": Spec("image", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, False),
        "image_preview": Spec("image", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, True),
        "ideology_image_one_display": Spec(
            "ideology_image_one", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, False
        ),
        "ideology_image_one_preview": Spec(
            "ideology_image_one", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, True
        ),
        "ideology_image_two_display": Spec(
            "ideology_image_two", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, False
        ),
        "ideology_image_two_preview": Spec(
            "ideology_image_two", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, True
        ),
    }

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        verbose_name = "Страница о компании"
        verbose_name_plural = "Страница о компании"


class Achievement(models.Model):
    """
    Достижение
    """

    value = models.CharField(verbose_name="Значение", max_length=50)
    title = models.CharField(verbose_name="Заголовок", max_length=50)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=50)

    about_section = models.ForeignKey(
        verbose_name="Страница о компании", to=AboutPage, on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"
        ordering = ("order",)


class IdeologyCard(models.Model, metaclass=MultiImageMeta):
    """
    Карточка идеологии
    """

    IMAGE_WIDTH = 439
    IMAGE_HEIGHT = 348

    title = models.CharField(verbose_name="Заголовок", max_length=100)
    text = RichTextField(verbose_name="Текст", max_length=1000)

    image = models.ImageField(
        verbose_name="Изображение 1", upload_to="c/c/i1", null=True, blank=True
    )

    about_section = models.ForeignKey(
        verbose_name="Страница о компании", to=AboutPage, on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(verbose_name="Порядок")

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Карточка идеологии"
        verbose_name_plural = "Карточки идеологии"
        ordering = ("order",)


class IdeologySlider(models.Model, metaclass=MultiImageMeta):
    """
    Слайдер идеологии
    """

    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 832

    text = RichTextField(verbose_name="Текст", max_length=1000)

    image = models.ImageField(
        verbose_name="Изображение", upload_to="ap/is/i", null=True, blank=True
    )

    about_section = models.ForeignKey(
        verbose_name="Страница о компании", to=AboutPage, on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(verbose_name="Порядок")

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return self._meta.verbose_name + str(self.order)

    class Meta:
        verbose_name = "Слайдер идеологии"
        verbose_name_plural = "Слайдеры идеологии"
        ordering = ("order",)


class LargeTenant(models.Model):
    """
    Крупный арендатор
    """

    name = models.CharField(verbose_name="Название", max_length=200)
    logo = models.FileField(verbose_name="Логотип", upload_to="ap/lt/l", blank=True, null=True)

    about_section = models.ForeignKey(
        verbose_name="Страница о компании", to=AboutPage, on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} '{self.name}'"

    class Meta:
        verbose_name = "Крупный арендатор"
        verbose_name_plural = "Крупные арендаторы"
        ordering = ("order",)


class CompanyValue(OrderedImage):
    """ Модель ценности компании """

    upload_to = "c/cv/i"

    WIDTH = 1920
    HEIGHT = 1080

    name = models.CharField("Название", max_length=64)
    text = models.TextField("Текст", blank=True)
    about_section = models.ForeignKey(
        "company.AboutPage", verbose_name="Страница о компании", on_delete=models.CASCADE
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Ценность компании"
        verbose_name_plural = "Ценности компании"

    def __str__(self):
        return self.name

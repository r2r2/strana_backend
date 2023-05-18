from ajaximage.fields import AjaxImageField
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from django.db import models
from common.constants import FULLSCREEN_HEIGHT, FULLSCREEN_WIDTH
from common.models import MultiImageMeta, Spec
from .constants import NewsType
from .querysets import NewsQuerySet


class News(models.Model, metaclass=MultiImageMeta):
    """
    Новость
    """

    CARD_IMAGE_WIDTH = 500
    CARD_IMAGE_HEIGHT = 425
    IMAGE_WIDTH = 1532
    IMAGE_HEIGHT = 864

    objects = NewsQuerySet.as_manager()

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    link = models.URLField(
        verbose_name="Ссылка", help_text="Для камеры", max_length=200, null=True, blank=True
    )
    slug = models.SlugField(verbose_name="Алиас", unique=True)
    type = models.CharField(verbose_name="Тип", max_length=20, choices=NewsType.choices)
    intro = models.TextField(verbose_name="Анонс", blank=True)
    short_description = models.TextField(
        verbose_name="Краткое описание", blank=True, help_text="Для страницы проекта"
    )
    text = RichTextUploadingField(verbose_name="Текст новости/акции", blank=True)
    published = models.BooleanField(verbose_name="Опубликовано", default=False, db_index=True)
    is_display_flat_listing = models.BooleanField(
        verbose_name="Отображать в листинге квартир", help_text="Для акций", default=False
    )
    colored_title = models.CharField(
        verbose_name="Цветной заголовок", max_length=50, null=True, blank=True
    )
    video_url = models.TextField(verbose_name="URL для видео", blank=True)
    video_length = models.IntegerField(
        verbose_name="Продолжительность видео", default=0, help_text="В секундах"
    )

    start = models.DateTimeField(
        verbose_name="Дата публикации", null=True, blank=True, db_index=True
    )
    end = models.DateTimeField(
        verbose_name="Дата окончания",
        null=True,
        blank=True,
        db_index=True,
        help_text="Используется только для акций",
    )
    date = models.DateField(
        verbose_name="Дата события",
        null=True,
        blank=True,
        db_index=True,
        help_text="Используется для ходя строительства",
    )

    card_image = models.ImageField(
        verbose_name="Изображение на карточке",
        upload_to="news/images",
        blank=True,
        help_text=f"шир. - {CARD_IMAGE_WIDTH}, выс. - {CARD_IMAGE_HEIGHT}",
    )
    card_description = models.TextField(
        verbose_name="Описание на карточке", blank=True, help_text="Для акции в листинге квартир"
    )
    image = models.ImageField(
        verbose_name="Изображение новости/акции",
        upload_to="news/images",
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )

    projects = models.ManyToManyField(verbose_name="Проекты", to="projects.Project", blank=True)
    source_link = models.CharField(
        "Ссылка на источник", blank=True, max_length=264, help_text="Используется для СМИ о нас"
    )
    mass_media = models.ForeignKey(
        verbose_name="СМИ", to="news.MassMedia", on_delete=models.SET_NULL, blank=True, null=True
    )
    button_name = models.CharField(
        "Название кнопки",
        blank=True,
        help_text="На странице новости. Для вывода ссылки заполните дополнительно ссылку, а для формы - форму.",
        max_length=64,
    )
    button_link = models.CharField(
        "Ссылка кнопки",
        blank=True,
        max_length=255,
        help_text="Пример: /news/ -> strana.com/news/, для ссылки на внешний сайт, отметьте чекбокс ниже.",
    )
    button_blank = models.BooleanField("Открывать ссылку кнопки в новой вкладке", default=False)
    form = models.ForeignKey(
        verbose_name="Форма", to="news.NewsForm", on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)
    icon = models.ImageField(verbose_name="Иконка", upload_to="c/o/i", null=True, blank=True)
    
    image_map = {
        "card_image_display": Spec("card_image", CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT, False),
        "card_image_preview": Spec("card_image", CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT, True),
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"{self.type}: {self.title}"

    def clean(self) -> None:
        errors = {}
        if self.type in [NewsType.PROGRESS]:
            if not self.date:
                errors["date"] = "Для хода строительства необходимо указать дату"
        if errors:
            raise ValidationError(errors.get("form") or errors)

    @property
    def another_news(self) -> NewsQuerySet:
        if self.type in [NewsType.NEWS, NewsType.ACTION]:
            return News.objects.active().filter(type=self.type).annotate_color().exclude(pk=self.pk)
        return News.objects.none()

    def get_url(self):
        return f"https://strana.com/{self.type}/{self.slug}/"

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ("order",)


class NewsSlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд новости
    """

    IMAGE_WIDTH = 2880
    IMAGE_HEIGHT = 1192

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    video_url = models.TextField(verbose_name="URL для видео", blank=True)
    video_length = models.IntegerField(
        verbose_name="Продолжительность видео", default=0, help_text="В секундах"
    )

    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="news/images",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    preview = AjaxImageField(
        verbose_name="Превью видео",
        upload_to="news/videos",
        null=True,
        blank=True,
        help_text=f"шир. - {FULLSCREEN_WIDTH}, выс. - {FULLSCREEN_HEIGHT}",
    )
    video = models.FileField(verbose_name="Видео", null=True, blank=True, upload_to="news/videos")

    news = models.ForeignKey(verbose_name="Новость", to=News, on_delete=models.CASCADE)
    building = models.ForeignKey(
        verbose_name="Корпус",
        to="buildings.Building",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Если изображение относится к ходу строительства, можно указать соответсвующий корпус",
    )

    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_card_display": Spec("image", 500, 440, False),
        "image_card_preview": Spec("image", 500, 440, True),
        "preview_display": Spec("preview", FULLSCREEN_WIDTH / 4, FULLSCREEN_HEIGHT / 4, False),
        "preview_preview": Spec("preview", FULLSCREEN_WIDTH / 5, FULLSCREEN_HEIGHT / 5, True),
    }

    def clean(self) -> None:
        errors = {}
        if self.news.type != NewsType.PROGRESS and self.building:
            errors["building"] = (
                "Корпус может быть указан только у новости с типом '%s'" % NewsType.PROGRESS.label
            )
        if errors:
            raise ValidationError(errors.get("form") or errors)

    class Meta:
        verbose_name = "Слайды"
        verbose_name_plural = "Слайды"
        ordering = ("order",)


class MassMedia(models.Model):
    """Модель СМИ"""

    name = models.CharField("Название", max_length=64)
    logo = models.FileField("Логотип", blank=True, upload_to="news/mm")
    is_display_name = models.BooleanField("Выводить название СМИ", default=True)

    class Meta:
        verbose_name = "СМИ"
        verbose_name_plural = "СМИ"

    def __str__(self):
        return self.name


class NewsForm(models.Model):
    """Модель формы на странице новости"""

    title = models.CharField(verbose_name="Название", max_length=128)
    yandex_metrics = models.CharField(
        verbose_name="Яндекс метрика", max_length=100, null=True, blank=True
    )
    google_event_name = models.CharField("Название ивента Google", max_length=100, blank=True)

    class Meta:
        verbose_name = "Форма на странице новости"
        verbose_name_plural = "Формы на странице новости"

    def __str__(self):
        return self.title

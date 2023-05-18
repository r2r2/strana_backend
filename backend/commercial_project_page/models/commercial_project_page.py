from django.db import models

from common.models import Spec, MultiImageMeta
from ..querysets import CommercialProjectPageQuerySet


class CommercialProjectPage(models.Model, metaclass=MultiImageMeta):
    """ Модель страницы коммерческого проекта """

    ABOUT_IMAGE_WIDTH = 900
    ABOUT_IMAGE_HEIGHT = 1200

    objects = CommercialProjectPageQuerySet.as_manager()

    name = models.CharField(verbose_name="Название", max_length=200)
    slug = models.SlugField(verbose_name="Алиас", blank=True)
    project = models.OneToOneField(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    about_text = models.CharField(verbose_name="Текст о проекте", max_length=300, blank=True)
    about_text_colored = models.CharField(
        verbose_name="Выделенный тексто проекте", max_length=300, blank=True
    )
    about_image = models.ImageField(
        verbose_name="Изображение о проекте", upload_to="cpp/about_image", blank=True
    )
    video = models.URLField(verbose_name="Видео о проекте", blank=True)
    video_duration = models.CharField(
        verbose_name="Длительность видео", max_length=30, default="2:30"
    )
    video_preview = models.ImageField(
        verbose_name="Превью для видео",
        upload_to="cpp/video_preview", blank=True
    )
    invest_title = models.CharField(
        verbose_name="Заголовок блока инвестиций", blank=True, max_length=128
    )
    invest_subtitle = models.CharField(
        verbose_name="Подзаголовок блока инвестиций", blank=True, max_length=128
    )
    invest_text = models.TextField(verbose_name="Текст блока инвестиций", blank=True)
    form = models.ForeignKey(
        verbose_name="Форма",
        to="commercial_project_page.CommercialProjectPageForm",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    image_map = {
        "about_image_display": Spec(
            source="about_image", width=ABOUT_IMAGE_WIDTH, height=ABOUT_IMAGE_HEIGHT, default="png"
        ),
        "about_image_preview": Spec(
            source="about_image",
            width=ABOUT_IMAGE_WIDTH,
            height=ABOUT_IMAGE_HEIGHT,
            default="png",
            blur=True,
        ),
        "video_preview_preview": Spec(
            source="video_preview",
            width=ABOUT_IMAGE_WIDTH,
            height=ABOUT_IMAGE_HEIGHT,
            default="png", blur=True
        ),
        "video_preview_display": Spec(
            source="video_preview",
            width=ABOUT_IMAGE_WIDTH,
            height=ABOUT_IMAGE_HEIGHT,
            default="png",
        )
    }

    class Meta:
        verbose_name = "Страница коммерческого проекта"
        verbose_name_plural = "Страницы коммерческих проектов"

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} {self.project}"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self.project.slug
        super().save(*args, **kwargs)


class CommercialProjectPageForm(models.Model, metaclass=MultiImageMeta):
    """ Модель формы на странице коммерческого проекта """

    IMAGE_WIDTH = 900
    IMAGE_HEIGHT = 1200

    title = models.CharField(verbose_name="Заголовок формы", blank=True, max_length=120)
    text = models.TextField(verbose_name="Текст формы", blank=True)
    image = models.ImageField(verbose_name="Изображение формы", upload_to="cpp/fi", blank=True)

    image_map = {
        "image_display": Spec(source="image", width=IMAGE_WIDTH, height=IMAGE_HEIGHT),
        "image_preview": Spec(source="image", width=IMAGE_WIDTH, height=IMAGE_HEIGHT, blur=True),
    }

    class Meta:
        verbose_name = "Форма на странице коммерческого проекта"
        verbose_name_plural = "Формы на странице коммерческого проекта"

    def __str__(self):
        return self.title

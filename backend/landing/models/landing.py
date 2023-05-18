from ckeditor.fields import RichTextField
from django.db import models

from common.models import Spec, Page, MultiImageMeta, ActiveQuerySet


class Landing(Page, metaclass=MultiImageMeta):
    """Модель посадочной страницы"""

    WIDTH_MAIN_IMAGE = 3200
    HEIGHT_MAIN_IMAGE = 1900
    CARD_IMAGE_WIDTH = 960
    CARD_IMAGE_HEIGHT = 1120

    objects = ActiveQuerySet.as_manager()
    title = models.CharField("Заголовок главного экрана", max_length=128)
    slug = models.SlugField("Алиас", unique=True)
    is_active = models.BooleanField("Активен", default=True)
    is_promo = models.BooleanField("Промо-лендинг", default=False)
    text = RichTextField("Текст главного экрана", blank=True)

    main_image = models.ImageField(
        "Изображение главного экрана",
        upload_to="lnd/i",
        help_text=f"шир. - {WIDTH_MAIN_IMAGE}, выс. - {HEIGHT_MAIN_IMAGE}",
    )

    end = models.DateTimeField(
        verbose_name="Дата окончания акции",
        null=True,
        blank=True,
        db_index=True,
        help_text="Для промо-лендинга.",
    )
    projects = models.ManyToManyField(
        "projects.Project",
        verbose_name="Проекты",
        blank=True,
        help_text="Для промо-лендинга. Проекты будут установлены для связанной Новости",
    )

    landing_news = models.OneToOneField(
        "news.News",
        verbose_name="Новость лендинга",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    card_image = models.ImageField(
        verbose_name="Изображение на карточке",
        upload_to="news/images",
        blank=True,
        help_text=f"Для промо-лендинга. шир. - {CARD_IMAGE_WIDTH}, выс. - {CARD_IMAGE_HEIGHT}",
    )

    image_map = {
        "card_image_display": Spec("card_image", CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT, False),
        "card_image_preview": Spec("card_image", CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT, True),
        "main_image_display": Spec(
            source="main_image", width=WIDTH_MAIN_IMAGE, height=HEIGHT_MAIN_IMAGE
        ),
        "main_image_preview": Spec(
            source="main_image", width=WIDTH_MAIN_IMAGE, height=HEIGHT_MAIN_IMAGE, blur=True
        ),
    }

    class Meta:
        verbose_name = "Лендинг"
        verbose_name_plural = "Лендинги"

    def __str__(self):
        return self.title

from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.db import models
from cities.models import City
from common.constants import FULLSCREEN_HEIGHT, FULLSCREEN_WIDTH
from common.models import MultiImageMeta, OrderedImage, Spec
from ..queryset import CommercialPropertyPageQueryset


class CommercialPropertyPage(models.Model, metaclass=MultiImageMeta):
    """
    Страница коммерческой недвижимости
    """

    IMAGE_WIDTH = 1440
    IMAGE_HEIGHT = 1440

    objects = CommercialPropertyPageQueryset.as_manager()

    city = models.ForeignKey(verbose_name="Город", to=City, on_delete=models.CASCADE)
    is_page_hidden = models.BooleanField(
        verbose_name="Скрыть страницу для отображения", default=False
    )

    tenant_block_title = models.CharField("Заголовок блока арендаторов", max_length=200, blank=True)
    block_1_title = models.CharField(verbose_name="Блок 1 / Заголовок", max_length=200, blank=True)
    block_1_image_1 = AjaxImageField(
        verbose_name="Блок 1 / Изображение 1",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_1_image_2 = AjaxImageField(
        verbose_name="Блок 1 / Изображение 2",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_1_image_3 = AjaxImageField(
        verbose_name="Блок 1 / Изображение 3",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_1_image_4 = AjaxImageField(
        verbose_name="Блок 1 / Изображение 4",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_1_item_1_title = models.CharField(
        verbose_name="Блок 1 / Элемент 1 / Заголовок", max_length=200, blank=True
    )
    block_1_item_1_text = models.CharField(
        verbose_name="Блок 1 / Элемент 1 / Текст", max_length=200, blank=True
    )
    block_1_item_2_title = models.CharField(
        verbose_name="Блок 1 / Элемент 2 / Заголовок", max_length=200, blank=True
    )
    block_1_item_2_text = models.CharField(
        verbose_name="Блок 1 / Элемент 2 / Текст", max_length=200, blank=True
    )
    block_1_item_3_title = models.CharField(
        verbose_name="Блок 1 / Элемент 3 / Заголовок", max_length=200, blank=True
    )
    block_1_item_3_text = models.CharField(
        verbose_name="Блок 1 / Элемент 3 / Текст", max_length=200, blank=True
    )
    block_1_item_4_title = models.CharField(
        verbose_name="Блок 1 / Элемент 4 / Заголовок", max_length=200, blank=True
    )
    block_1_item_4_text = models.CharField(
        verbose_name="Блок 1 / Элемент 4 / Текст", max_length=200, blank=True
    )

    block_2_title = models.CharField(verbose_name="Блок 2 / Заголовок", max_length=200, blank=True)
    block_2_image_1 = AjaxImageField(
        verbose_name="Блок 2 / Изображение 1",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_2_image_2 = AjaxImageField(
        verbose_name="Блок 2 / Изображение 2",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_2_image_3 = AjaxImageField(
        verbose_name="Блок 2 / Изображение 3",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_2_image_4 = AjaxImageField(
        verbose_name="Блок 2 / Изображение 4",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    block_2_item_1_title = models.CharField(
        verbose_name="Блок 2 / Элемент 1 / Заголовок", max_length=200, blank=True
    )
    block_2_item_1_text = models.CharField(
        verbose_name="Блок 1 / Элемент 1 / Текст", max_length=200, blank=True
    )
    block_2_item_2_title = models.CharField(
        verbose_name="Блок 2 / Элемент 2 / Заголовок", max_length=200, blank=True
    )
    block_2_item_2_text = models.CharField(
        verbose_name="Блок 1 / Элемент 2 / Текст", max_length=200, blank=True
    )
    block_2_item_3_title = models.CharField(
        verbose_name="Блок 2 / Элемент 3 / Заголовок", max_length=200, blank=True
    )
    block_2_item_3_text = models.CharField(
        verbose_name="Блок 1 / Элемент 3 / Текст", max_length=200, blank=True
    )
    block_2_item_4_title = models.CharField(
        verbose_name="Блок 2 / Элемент 4 / Заголовок", max_length=200, blank=True
    )
    block_2_item_4_text = models.CharField(
        verbose_name="Блок 1 / Элемент 4 / Текст", max_length=200, blank=True
    )

    video = models.CharField(verbose_name="сылка на видео", max_length=2000, blank=True)

    video_preview = AjaxImageField(
        verbose_name="Видео / Превью",
        upload_to="commercial_property_page/image",
        null=True,
        blank=True,
        help_text=f"шир. - {FULLSCREEN_WIDTH}, выс. - {FULLSCREEN_HEIGHT}",
    )
    video_title = models.CharField(verbose_name="Видео / Заголовок", max_length=200, blank=True)
    video_description = models.TextField(verbose_name="Видео / Описание", blank=True)

    furnish_set = models.ManyToManyField(
        verbose_name="Варианты отделки", to="properties.Furnish", blank=True
    )

    furnish_kitchen_set = models.ManyToManyField(
        verbose_name="Варианты отделки кухни", to="properties.FurnishKitchen", blank=True
    )

    image_map = {
        "block_one_image_one_display": Spec("block_1_image_1", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_one_image_one_preview": Spec("block_1_image_1", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_one_image_two_display": Spec("block_1_image_2", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_one_image_two_preview": Spec("block_1_image_2", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_one_image_three_display": Spec("block_1_image_3", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_one_image_three_preview": Spec("block_1_image_3", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_one_image_four_display": Spec("block_1_image_4", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_one_image_four_preview": Spec("block_1_image_4", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_two_image_one_display": Spec("block_2_image_1", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_two_image_one_preview": Spec("block_2_image_1", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_two_image_two_display": Spec("block_2_image_2", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_two_image_two_preview": Spec("block_2_image_2", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_two_image_three_display": Spec("block_2_image_3", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_two_image_three_preview": Spec("block_2_image_3", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "block_two_image_four_display": Spec("block_2_image_4", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "block_two_image_four_preview": Spec("block_2_image_4", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "video_preview_display": Spec("video_preview", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, False),
        "video_preview_preview": Spec("video_preview", FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} - {self.city}"

    class Meta:
        verbose_name = "Страница коммерческой недвижимости"
        verbose_name_plural = "Страницы коммерческой недвижимости"


class CommercialPropertyPageSlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд страницы коммерческой недвижимости
    """

    WIDTH = 2880
    HEIGHT = 1090

    page = models.ForeignKey(
        verbose_name="Страница коммерческой недвижимости",
        to=CommercialPropertyPage,
        on_delete=models.CASCADE,
        related_name="slide_set",
    )
    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="commercial_property_page/slide",
        blank=True,
        null=True,
    )
    video_link = models.URLField(verbose_name="Ссылка на видео", blank=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return f"Слайд {self.id}"

    class Meta:
        verbose_name = "Слайд на странице коммерческой недвижимости"
        verbose_name_plural = "Слайды на странице коммерческой недвижимости"
        ordering = ("order",)


class CommercialPropertyPageAdvantage(OrderedImage, metaclass=MultiImageMeta):
    """
    Преимущество на странице коммерческой недвижимости
    """

    upload_to = "commercial_property_page/image"
    WIDTH = 486
    HEIGHT = 464

    page = models.ForeignKey(
        verbose_name="Страница коммерческой недвижимости",
        to=CommercialPropertyPage,
        on_delete=models.CASCADE,
        related_name="advantage_set",
    )
    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    text = RichTextField(verbose_name="Текст", blank=True)

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return f"Преимущество {self.id}"

    class Meta:
        verbose_name = "Преимущество на странице коммерческой недвижимости"
        verbose_name_plural = "Преимущества на странице коммерческой недвижимости"
        ordering = ("order",)

from ajaximage.fields import AjaxImageField
from django.core.exceptions import ValidationError
from django.db import models
from ckeditor.fields import RichTextField
from common.models import MultiImageMeta, Spec


class PurchaseAmount(models.Model):
    """
    Размер оплаты
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Размер оплаты"
        verbose_name_plural = "Размеры оплаты"
        ordering = ("id",)


class PurchaseAmountDescriptionBlock(models.Model):
    """
    Размер оплаты, блок описания
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    amount = models.ForeignKey(
        verbose_name="Размер оплаты", to=PurchaseAmount, on_delete=models.CASCADE
    )
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=200, blank=True)
    show_regional_block = models.BooleanField(
        verbose_name="Выводить в блоке региональный", default=False
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Размер оплаты, блок описания"
        verbose_name_plural = "Размер оплаты, блоки описания"
        ordering = ("id",)


class PurchaseTypeCategory(models.Model):
    """
    Категория способов покупки
    """

    name = models.CharField(verbose_name="Имя", max_length=100)
    slug = models.SlugField(verbose_name="Слаг", unique=True, null=True, blank=True)
    is_active = models.BooleanField(verbose_name="Активно", default=True)

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Категория способов покупки"
        verbose_name_plural = "Категории способов покупки"
        ordering = ("order",)


class PurchaseType(models.Model, metaclass=MultiImageMeta):
    """
    Способ покупки
    """

    DISPLAY_WIDTH = 2880
    DISPLAY_HEIGHT = 1800
    name = models.CharField(verbose_name="Название", max_length=200, null=True, blank=True)
    title_1 = models.CharField(verbose_name="Заголовок 1", max_length=200, null=True, blank=True)
    title_2 = models.CharField(verbose_name="Заголовок 2", max_length=200, null=True, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    description_document = RichTextField(verbose_name="Описание для документов", blank=True)
    link_text = models.CharField(verbose_name="Текст ссылки", max_length=100, blank=True)
    icon = AjaxImageField(verbose_name="Иконка", upload_to="purchase/icon", blank=True)
    image = models.ImageField(
        verbose_name="Главная картинка", upload_to="purchase/image", null=True, blank=True
    )
    is_commercial = models.BooleanField(verbose_name="Для страницы коммерции", default=False)

    city = models.ForeignKey(
        verbose_name="Город", to="cities.City", on_delete=models.CASCADE, blank=True, null=True
    )
    category = models.ForeignKey(
        verbose_name="Категория",
        to=PurchaseTypeCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    amount = models.ForeignKey(
        verbose_name="Размер оплаты",
        to=PurchaseAmount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    faq = models.ManyToManyField(
        to="purchase.PurchaseFAQ",
        verbose_name="FAQ",
        blank=True,
    )
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)
    show_calk = models.BooleanField("Отображать калькулятор", default=False)

    # Purchase type step block
    purchase_type_step_title = models.CharField(
        verbose_name="Заголовок шагов покупки", max_length=200, null=True, blank=True
    )
    purchase_type_step_description = RichTextField(
        verbose_name="Описание шагов покупки", null=True, blank=True
    )
    purchase_type_step_footer = RichTextField(
        verbose_name="Футер шагов покупки", null=True, blank=True
    )
    purchase_type_step_button = models.CharField(
        verbose_name="Текст кнопки шагов покупки", max_length=200, null=True, blank=True
    )
    image_map = {
        "image_display": Spec(source="image", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT),
        "image_preview": Spec(
            source="image", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, blur=True
        ),
    }

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if not self.category:
            raise ValidationError("Необходимо указать категорию")

    class Meta:
        verbose_name = "Способ покупки"
        verbose_name_plural = "Способы покупки"
        ordering = ("order",)
        unique_together = ("city", "category")


class PurchaseTypeStep(models.Model):
    """
    Шаг способа покупки
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = models.TextField(verbose_name="Описание", blank=True)

    purchase_type = models.ForeignKey(
        verbose_name="Способ покупки", to=PurchaseType, on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    class Meta:
        verbose_name = "Шаг способа покупки"
        verbose_name_plural = "Шаги способа покупки"
        ordering = ("order",)


class PurchaseFAQ(models.Model):
    question = models.TextField(
        verbose_name="Вопрос",
    )
    answer = models.TextField(
        verbose_name="Ответ",
    )

    class Meta:
        verbose_name_plural = verbose_name = "FAQ по способу покупки"

    def __str__(self):
        return self.question

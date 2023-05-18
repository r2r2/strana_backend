from django.db import models
from cities.models import City
from common.fields import FloatRangeField, IntegerRangeField
from common.models import MultiImageMeta, Spec
from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from ..constants import MortgageType
from ..queryset import OfferQuerySet
from .program import Program


class Offer(models.Model, metaclass=MultiImageMeta):
    """
    Предложение по ипотеке
    """
    DISPLAY_WIDTH = 2880
    DISPLAY_HEIGHT = 1800

    objects = OfferQuerySet.as_manager()

    is_active = models.BooleanField(verbose_name="Активное", default=True)
    is_site = models.BooleanField(verbose_name="Отображать предложение на сайте", default=False)
    type = models.CharField(verbose_name="Тип", max_length=100, choices=MortgageType.choices)
    deposit = FloatRangeField(verbose_name="Первоначальный взнос", blank=True, null=True)
    rate = FloatRangeField(verbose_name="Процентная ставка", blank=True, null=True)
    term = FloatRangeField(verbose_name="Срок кредита", blank=True, null=True)
    amount = IntegerRangeField(verbose_name="Сумма кредита", blank=True, null=True)
    subs_rate = FloatRangeField(
        verbose_name="Процентная ставка (субсидированная ипотека)", blank=True, null=True
    )
    subs_term = FloatRangeField(
        verbose_name="Срок кредита (субсидированная ипотека)", blank=True, null=True
    )
    program = models.ForeignKey(
        verbose_name="Программа", to=Program, on_delete=models.CASCADE, null=True, blank=True
    )
    city = models.ForeignKey(
        verbose_name="Город", to=City, on_delete=models.CASCADE, null=True, blank=True
    )
    projects = models.ManyToManyField(verbose_name="Проекты", to="projects.Project", blank=True)

    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

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
    faq = models.ManyToManyField(
        to="OfferFAQ",
        verbose_name="FAQ",
        blank=True,
    )

    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Предложение {self.id}"

    class Meta:
        verbose_name = "Предложение по ипотеке"
        verbose_name_plural = "Предложения по ипотеке"
        get_latest_by = "rate"
        ordering = ("order",)


class OfferTypeStep(models.Model):
    """
    Шаг способа покупки
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = models.TextField(verbose_name="Описание", blank=True)

    purchase_type = models.ForeignKey(
        verbose_name="Способ покупки", to=Offer, on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    class Meta:
        verbose_name = "Шаг способа покупки"
        verbose_name_plural = "Шаги способа покупки"
        ordering = ("order",)


class OfferFAQ(models.Model):
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
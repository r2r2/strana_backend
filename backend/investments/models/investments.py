from django.db import models
from ckeditor.fields import RichTextField
from ajaximage.fields import AjaxImageField

from ..constants import ControlComplexityLevel, LiquidDifficultyLevel
from common.models import MultiImageMeta, Spec


class YieldComparison(models.Model):
    rent = models.CharField(max_length=255, verbose_name='Сдача в аренду')
    rent_show = models.BooleanField(default=False, verbose_name='Выделяем сдачу в аренду')
    quadrature = models.CharField(max_length=255, verbose_name='Квадратура')
    quadrature_show = models.BooleanField(default=False, verbose_name='Выделяем квадратуру')
    price = models.CharField(max_length=255, verbose_name='Стоимость')
    price_show = models.BooleanField(default=False, verbose_name='Выделяем стоимость')
    repair = models.CharField(max_length=255, verbose_name='Ремонт')
    repair_show = models.BooleanField(default=False, verbose_name='Выделяем ремонт')
    appliances_and_furniture = models.CharField(max_length=255, verbose_name='Мебель и техника')
    appliances_and_furniture_show = models.BooleanField(default=False, verbose_name='Выделяем медель и технику')
    attachments = models.CharField(max_length=255, verbose_name='Вложения')
    attachments_show = models.BooleanField(default=False, verbose_name='Выделяем вложения')
    rental_income = models.CharField(max_length=255, verbose_name='Доход от ренты')
    rental_income_show = models.BooleanField(default=False, verbose_name='Выделяем доход от ренты')
    payback = models.CharField(max_length=255, verbose_name='Окупаемость')
    payback_show = models.BooleanField(default=False, verbose_name='Выделяем окупаемость')
    in_percent = models.CharField(max_length=255, verbose_name='% годовых')
    in_percent_show = models.BooleanField(default=False, verbose_name='Выделяем % годовых')
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", blank=True, null=True)

    def __str__(self):
        return f'{self.rent}'

    class Meta:
        verbose_name = "Примеры сранения доходности"
        verbose_name_plural = "Примеры сранений доходности"


class InvestmentTypes(models.Model):
    investment_types = models.CharField(verbose_name='Вид инвестиций', max_length=255)
    income = models.CharField(verbose_name='Доходность', max_length=255)
    risks = models.CharField(verbose_name='Риски', max_length=255)
    risks_alt = models.CharField(verbose_name='Описание рисков', max_length=255, blank=True, null=True)
    management_complexity = models.CharField(
        verbose_name='Легкость в управлении',
        max_length=255,
        choices=ControlComplexityLevel.choices
    )
    liquidity = models.CharField(
        verbose_name='Ликвидность',
        max_length=255,
        choices=LiquidDifficultyLevel.choices
    )
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", blank=True, null=True)

    def __str__(self):
        return f'{self.investment_types}'

    class Meta:
        verbose_name = "Сравнение видов инвестиций"
        verbose_name_plural = "Сравнение видов инвестиций"


class RentalBusinessSales(models.Model):
    price = models.CharField(max_length=255, verbose_name='Цена объекта')
    quadrature = models.CharField(max_length=255, verbose_name='Квадратура')
    month_rent = models.CharField(max_length=255, verbose_name='Аренда в месяц')
    year_rent = models.CharField(max_length=255, verbose_name='Аренда в год')
    payback = models.CharField(max_length=255, verbose_name='Окупаемость')
    in_percent = models.CharField(max_length=255, verbose_name='% годовых')
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", blank=True, null=True)

    def __str__(self):
        return f'{self.price}'

    class Meta:
        verbose_name = "Кейсы продажи арендного бизнеса"
        verbose_name_plural = "Кейсы продажи арендного бизнеса"


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class MainBanner(SingletonModel):
    block_name = models.CharField(verbose_name="Название блока", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)
    button_name = models.CharField(verbose_name="Надпись на кнопке", max_length=255, blank=True, null=True)
    picture = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")

    def __str__(self):
        return f'{self.block_name}'

    class Meta:
        verbose_name = "Главный баннер"
        verbose_name_plural = "Главный баннер"


class Banner(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    icon = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"


class SecondBanner(SingletonModel):
    title = RichTextField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    picture = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Второй блок"
        verbose_name_plural = "Второй блок"


class LastBanner(SingletonModel):
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=255, blank=True, null=True)
    icon_1 = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")
    icon_2 = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")
    othertitle_1 = models.CharField(verbose_name="Другой заголовок 1", max_length=255, blank=True, null=True)
    othertitle_2 = models.CharField(verbose_name="Другой заголовок 2", max_length=255, blank=True, null=True)
    othersubtitle_1 = models.CharField(verbose_name="Другой подзаголовок 1", max_length=255, blank=True, null=True)
    othersubtitle_2 = models.CharField(verbose_name="Другой подзаголовок 2", max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Данные на третьем блоке"
        verbose_name_plural = "Данные на третьем блоке"


class OwnEyeLooking(SingletonModel, metaclass=MultiImageMeta):
    """
    Кастомная форма
    """

    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 906
    IMAGE_PHONE_WIDTH = 112
    IMAGE_PHONE_HEIGHT = 112

    name = models.CharField(verbose_name="Название", max_length=200)
    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    success = models.CharField(
        verbose_name="Сообщение при успешной отправке", max_length=200, blank=True
    )
    button_text = models.CharField(verbose_name="Текст на кнопке", max_length=200, blank=True)
    active = models.BooleanField(verbose_name="Активна", default=False)
    type_form = models.CharField("Тип для обработки запроса", blank=True, max_length=200)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    yandex_metrics = models.CharField(
        verbose_name="Яндекс метрика", max_length=100, null=True, blank=True
    )
    google_event_name = models.CharField("Название ивента Google", max_length=100, blank=True)
    full_name = models.CharField(verbose_name="ФИО", max_length=200, blank=True)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    image = AjaxImageField(verbose_name="Изображение", upload_to="f/i", null=True, blank=True)
    image_phone = models.ImageField(
        verbose_name="Мобильное изображение", upload_to="f/ip", null=True, blank=True
    )

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_phone_display": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, False),
        "image_phone_preview": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, True),
    }
    
    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Посмотрите своими глазами"
        verbose_name_plural = "Посмотрите своими глазами"

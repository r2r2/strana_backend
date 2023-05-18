from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from cities.models import City
from common.models import MultiImageMeta, Spec
from projects.models import Project
from .queryset import OfficeQuerySet


class Office(models.Model, metaclass=MultiImageMeta):
    """
    Офис
    """

    ICON_WIDTH = 960
    ICON_HEIGHT = 640

    objects = OfficeQuerySet.as_manager()

    cities = models.ManyToManyField(verbose_name="Города", to=City, blank=True)
    city = models.ForeignKey(
        verbose_name="Город",
        blank=True,
        null=True,
        to=City,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Выводится на карточке офиса. Если не заполнен, выводятся 'Города'",
    )
    projects = models.ManyToManyField(verbose_name="Проекты", to=Project, blank=True)

    icon = models.ImageField(verbose_name="Иконка", upload_to="c/o/i", null=True, blank=True)
    active = models.BooleanField(verbose_name="Активный", default=True, db_index=True)
    name = models.CharField(verbose_name="Название", max_length=200, blank=True)
    address = models.CharField(verbose_name="Адрес", max_length=200, blank=True)
    phone = PhoneNumberField(verbose_name="Телефон", blank=True, null=True)
    email = models.EmailField(verbose_name="Адрес электронной почты", blank=True)
    work_time = models.CharField(verbose_name="Часы работы", max_length=200, blank=True)
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    is_central = models.BooleanField(verbose_name="Центральный", default=False)
    is_commercial = models.BooleanField(
        verbose_name="Коммерческий",
        default=False,
        help_text="Выводить офис на странице коммерции проекта",
    )

    latitude = models.DecimalField(
        verbose_name="Широта", max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        verbose_name="Долгота", max_digits=9, decimal_places=6, blank=True, null=True
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", null=True, blank=True)

    image_map = {
        "icon_display": Spec("icon", ICON_WIDTH, ICON_HEIGHT, False),
        "icon_preview": Spec("icon", ICON_WIDTH, ICON_HEIGHT, True),
    }

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Офис"
        verbose_name_plural = "Офисы"
        ordering = ("order",)


class Subdivision(models.Model, metaclass=MultiImageMeta):
    """
    Подразделение
    """

    ICON_WIDTH = 88
    ICON_HEIGHT = 88

    office = models.ForeignKey(verbose_name="Офис", to=Office, on_delete=models.CASCADE)

    icon = models.ImageField(verbose_name="Иконка", upload_to="c/s/i", null=True, blank=True)
    active = models.BooleanField(verbose_name="Активный", default=True, db_index=True)
    name = models.CharField(verbose_name="Название", max_length=200, blank=True)
    phone = PhoneNumberField(verbose_name="Телефон", blank=True, null=True)
    email = models.EmailField(verbose_name="Адрес электронной почты", blank=True)

    image_map = {
        "icon_display": Spec("icon", ICON_WIDTH, ICON_HEIGHT, False),
        "icon_preview": Spec("icon", ICON_WIDTH, ICON_HEIGHT, True),
    }

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"


class Social(models.Model):
    """
    Социцальная сеть
    """

    name = models.CharField(verbose_name="Имя", max_length=50)
    link = models.URLField(verbose_name="Ссылка", max_length=1000)
    share_link = models.CharField(verbose_name="Ссылка для шеринга", max_length=1000, blank=True)

    icon = models.FileField(verbose_name="Иконка", upload_to="c/s/i", blank=True, null=True)
    colored_icon = models.FileField(
        verbose_name="Цветная иконка", upload_to="c/s/ci", blank=True, null=True
    )
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    colored_icon_content = models.TextField(
        verbose_name="Контент цветной иконки", null=True, blank=True
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"
        ordering = ("order",)

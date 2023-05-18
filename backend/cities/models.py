from colorful.fields import RGBColorField
from ckeditor.fields import RichTextField
from django.core.files.storage import default_storage
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from cities.querysets import CityManager, CityQuerySet
from common.fields import PpoiField
from common.models import MultiImageMeta, Spec

from main_page.querysets import MainPageSlideQuerySet


class City(models.Model, metaclass=MultiImageMeta):
    """
    Город
    """

    objects = CityQuerySet.as_manager()

    name = models.CharField(verbose_name="Название", max_length=100)
    short_name = models.CharField(
        verbose_name="Короткое название", max_length=50, null=True, blank=True
    )
    slug = models.CharField(verbose_name="Слаг", max_length=100, blank=True)
    color = RGBColorField(verbose_name="Цвет", default="#FFFFFF", max_length=8)
    phone = PhoneNumberField(verbose_name="Телефон", null=True, blank=True)
    active = models.BooleanField(verbose_name="Активный", default=True, db_index=True)
    disable_site = models.BooleanField(
        verbose_name="Деактивировать ссылку на сайт города", default=False, db_index=True
    )
    is_without_lots = models.BooleanField(
        verbose_name="Город без лотов", default=False, help_text="Скрывает функционал на фронте"
    )
    is_region = models.BooleanField(
        verbose_name="Область", default=False, help_text="Скрывает на карте"
    )
    is_only_map = models.BooleanField(
        verbose_name="Отображать город только на карте", default=False
    )
    map_name = models.CharField(verbose_name="Название на карте", max_length=128, blank=True)

    latitude = models.DecimalField(
        verbose_name="Широта", decimal_places=6, max_digits=9, null=True, blank=True
    )
    longitude = models.DecimalField(
        verbose_name="Долгота", decimal_places=6, max_digits=9, null=True, blank=True
    )

    local_coords = PpoiField(
        verbose_name="Точка на генплане", source="map.image_desktop", null=True, blank=True
    )
    commercial_image = models.ImageField(
        verbose_name="Коммерческое изображение", upload_to="c/c/ci", null=True, blank=True
    )

    address = models.CharField(verbose_name="Адрес", max_length=100, null=True, blank=True)
    working_time = models.CharField(
        verbose_name="Режим работы", max_length=100, null=True, blank=True
    )

    app_store_link = models.URLField(
        verbose_name="Ссылка AppStore", max_length=200, null=True, blank=True
    )
    google_play_link = models.URLField(
        verbose_name="Ссылка GooglePlay", max_length=200, null=True, blank=True
    )

    min_mortgage_commercial = models.FloatField(
        verbose_name="Мин коммерческая ипотека", null=True, blank=True
    )
    min_mortgage_residential = models.FloatField(
        verbose_name="Мин жилая ипотека", null=True, blank=True
    )
    min_mortgage_residential_standard = models.FloatField(
        verbose_name="Мин жилая ипотека(Стандартная программа)", null=True, blank=True
    )
    min_mortgage_residential_support = models.FloatField(
        verbose_name="Мин жилая ипотека(Господдержка)", null=True, blank=True
    )
    min_mortgage_residential_family = models.FloatField(
        verbose_name="Мин жилая ипотека(Семейная ипотека)", null=True, blank=True
    )
    flats_0_min_price = models.DecimalField(
        verbose_name="Мин цена студия", max_digits=14, decimal_places=2, null=True, blank=True
    )
    flats_1_min_price = models.DecimalField(
        verbose_name="Мин цена 1-комн", max_digits=14, decimal_places=2, null=True, blank=True
    )
    flats_2_min_price = models.DecimalField(
        verbose_name="Мин цена 2-комн", max_digits=14, decimal_places=2, null=True, blank=True
    )
    flats_3_min_price = models.DecimalField(
        verbose_name="Мин цена 3-комн", max_digits=14, decimal_places=2, null=True, blank=True
    )
    flats_4_min_price = models.DecimalField(
        verbose_name="Мин цена 4-комн", max_digits=14, decimal_places=2, null=True, blank=True
    )
    min_commercial_price = models.DecimalField(
        verbose_name="Мин цена коммерция", max_digits=14, decimal_places=2, null=True, blank=True
    )
    min_commercial_price_divided = models.DecimalField(
        verbose_name="Мин цена коммерция поделенная",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    min_commercial_area = models.DecimalField(
        verbose_name="Мин площадь коммерция", max_digits=8, decimal_places=2, null=True, blank=True
    )
    max_commercial_area = models.DecimalField(
        verbose_name="Макс площадь коммерция", max_digits=8, decimal_places=2, null=True, blank=True
    )

    site = models.OneToOneField(verbose_name="Сайт", to="sites.Site", on_delete=models.CASCADE)
    map = models.ForeignKey(
        verbose_name="Карта",
        to="cities.Map",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=1,
    )
    header_popup_text = models.TextField(
        verbose_name="Текст верхнего баннера в шапке",
        null=True,
        blank=True,
    )
    header_popup_url = models.URLField(
        verbose_name="Ссылка верхнего баннера в шапке",
        null=True,
        blank=True,
    )
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=True, db_index=True)

    image_map = {
        "commercial_image_display": Spec(source="commercial_image", width=962, height=498),
        "commercial_image_preview": Spec(
            source="commercial_image", width=481, height=249, blur=True
        ),
    }
    amocrm_enum = models.PositiveIntegerField(
        verbose_name="ID города в AmoCRM",
        null=True, default=None, blank=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ("order",)


class ProjectSlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд на проектах
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
        to=City,
        on_delete=models.CASCADE,
        related_name="project_slides",
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
        return f"Слайд на проектах {self.id}"

    class Meta:
        verbose_name = "Слайд на проектах"
        verbose_name_plural = "Слайд на проектах"
        ordering = ("order",)


class MetroLine(models.Model):
    """
    Линия метро
    """

    name = models.CharField(verbose_name="Название", max_length=255)
    color = RGBColorField(verbose_name="Цвет", default="#FF0000", blank=True)

    city = models.ForeignKey(verbose_name="Город", to=City, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Линия метро"
        verbose_name_plural = "Линии метро"

    def __str__(self) -> str:
        return self.name


class Metro(models.Model):
    """
    Станция метро
    """

    name = models.CharField(verbose_name="Название", max_length=32)

    latitude = models.DecimalField(
        verbose_name="Широта", decimal_places=6, max_digits=9, null=True, blank=True
    )
    longitude = models.DecimalField(
        verbose_name="Долгота", decimal_places=6, max_digits=9, null=True, blank=True
    )

    line = models.ForeignKey(verbose_name="Линия метро", to=MetroLine, on_delete=models.CASCADE)

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Станция метро"
        verbose_name_plural = "Станции метро"
        ordering = ("order",)


class Transport(models.Model):
    """
    Способ передвижения
    """

    name = models.CharField(verbose_name="Название", max_length=100)
    icon = models.FileField(verbose_name="Иконка", upload_to="c/t/i", null=True, blank=True)
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.icon:
            with default_storage.open(self.icon.name) as icon_file:
                icon_content = icon_file.read().decode("utf-8")
            Transport.objects.filter(id=self.id).update(icon_content=icon_content)
            self.refresh_from_db()

    class Meta:
        verbose_name = "Способ передвижения"
        verbose_name_plural = "Способы передвижения"


class Map(models.Model, metaclass=MultiImageMeta):
    """
    Карта
    """

    DESKTOP_WIDTH = 2880
    DESKTOP_HEIGHT = 1800
    TABLET_HEIGHT = 960
    TABLET_WIDTH = 1536
    MOBILE_WIDTH = 960
    MOBILE_HEIGHT = 640

    name = models.CharField(verbose_name="Имя", max_length=100, null=True, blank=True)
    slug = models.SlugField(verbose_name="Слаг", max_length=100, unique=True)
    is_main = models.BooleanField(verbose_name="Главная", default=False)

    image_desktop = models.ImageField(
        verbose_name="Изображение десктоп", upload_to="m/m/id", null=True, blank=True
    )
    image_tablet = models.ImageField(
        verbose_name="Изображение планшет", upload_to="m/m/it", null=True, blank=True
    )
    image_phone = models.ImageField(
        verbose_name="Изображение телефон", upload_to="m/m/ip", null=True, blank=True
    )

    image_map = {
        "image_desktop_display": Spec(
            source="image_desktop", width=DESKTOP_WIDTH, height=DESKTOP_HEIGHT
        ),
        "image_tablet_display": Spec(
            source="image_tablet", width=TABLET_WIDTH, height=TABLET_HEIGHT
        ),
        "image_phone_display": Spec(source="image_phone", width=MOBILE_WIDTH, height=MOBILE_HEIGHT),
        "image_desktop_preview": Spec(
            source="image_desktop", width=DESKTOP_WIDTH, height=DESKTOP_HEIGHT, blur=True
        ),
        "image_tablet_preview": Spec(
            source="image_tablet", width=TABLET_WIDTH, height=TABLET_HEIGHT, blur=True
        ),
        "image_phone_preview": Spec(
            source="image_phone", width=MOBILE_WIDTH, height=MOBILE_HEIGHT, blur=True
        ),
    }

    def __str__(self) -> str:
        if self.name:
            return self.name
        return self.slug

    class Meta:
        verbose_name = "Карта"
        verbose_name_plural = "Карты"

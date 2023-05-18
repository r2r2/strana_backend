from ajaximage.fields import AjaxImageField
from colorful.fields import RGBColorField
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

from cities.models import Metro, Transport
from common.models import MultiImageMeta, Spec
from projects.querysets import ProjectQuerySet

from ..constants import ProjectSkyColor, ProjectStatusType, ProjectTemplateTypeChoices
from .project_ideology import ProjectIdeology


class Project(models.Model, metaclass=MultiImageMeta):
    """
    Проект
    """

    PLAN_DISPLAY_WIDTH = 2880
    PLAN_DISPLAY_HEIGHT = 1800

    objects = ProjectQuerySet.as_manager()
    template_type = models.CharField(
        "Тип шаблона",
        choices=ProjectTemplateTypeChoices.choices,
        default=ProjectTemplateTypeChoices.COMFORT,
        max_length=20,
    )

    name = models.CharField(verbose_name="Название", max_length=200)
    redirect_link = models.URLField(verbose_name="Ссылка для перехода", blank=True)
    is_redirect = models.BooleanField(verbose_name="Функционал перехода", default=False)
    button_name = models.CharField(verbose_name="Название кнопки", max_length=200, blank=True)
    button_link = models.URLField(verbose_name="Ссылка для перехода по кнопке", blank=True)
    button_is_redirect = models.BooleanField(
        verbose_name="Функционал перехода по кнопке", default=False
    )
    tour_title = models.CharField(verbose_name="Заголовок 3D тура", max_length=200, blank=True)
    tour_text = models.CharField(verbose_name="Текст 3D тура", max_length=200, blank=True)
    tour_img = models.ImageField(
        "Изображение 3D тура", upload_to="p/p/tour", blank=True, null=True
    )
    tour_link = models.URLField(verbose_name="Ссылка для 3D тура", blank=True)

    slug = models.SlugField(verbose_name="Алиас", blank=True)

    is_button_presentation = models.BooleanField(verbose_name="Кнопка регистрации на презентацию", default=False)

    is_residential = models.BooleanField(verbose_name="Жилой", default=False)
    is_commercial = models.BooleanField(verbose_name="Коммерческий", default=False)
    is_soon = models.BooleanField(
        verbose_name="Скоро", default=False, help_text="Добавляет текст на карточку"
    )
    is_completed = models.BooleanField(
        verbose_name="Сдан", default=False, help_text="Добавляет текст на карточку"
    )
    is_display_future_on_map = models.BooleanField(
        verbose_name="Выводить будущий проект на карту", default=False
    )
    deadline = models.DateField(verbose_name="Срок сдачи", null=True, blank=True)
    commercial_title = models.CharField(verbose_name="Заголовок блока Коммерция", max_length=200, blank=True)
    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    address = models.TextField(verbose_name="Адрес", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    parking_title = models.CharField(
        verbose_name="Заголовок блока 'Паркинг'", blank=True, max_length=128
    )
    parking_text = models.TextField(verbose_name="Текст блока 'Паркинг'", blank=True)
    parking_image = models.ImageField(
        verbose_name="Изображение блока 'Паркинг'", blank=True, upload_to="p/pi"
    )
    active = models.BooleanField(verbose_name="Активен", default=False, db_index=True)
    changed = models.DateField(verbose_name="Изменено", auto_now=True)
    launch_date = models.DateField(
        verbose_name="Планируемая дата старта проекта", blank=True, null=True
    )
    start_sales = models.DateField(verbose_name="Дата старта продаж", blank=True, null=True)
    commissioning_year = models.IntegerField(
        verbose_name="Год ввода в эксплуатацию", blank=True, null=True
    )
    total_area = models.FloatField(
        verbose_name="Общая площадь проекта", help_text="В квадратных метрах", blank=True, null=True
    )
    hash = models.BinaryField(verbose_name="Хэш", max_length=20, null=True, blank=True)
    image = AjaxImageField(verbose_name="Изображение", upload_to="p/image", blank=True, null=True)
    transport_time = models.PositiveSmallIntegerField(
        verbose_name="Время в пути", blank=True, null=True
    )
    project_color = RGBColorField(verbose_name="Цвет", default="#FFFFFF", max_length=8)
    card_sky_color = models.CharField(
        "Цвет неба на карточке проекта",
        choices=ProjectSkyColor.choices,
        default=ProjectSkyColor.LIGHT_BLUE,
        max_length=20,
    )
    card_link = models.CharField(
        verbose_name="Ссылка на карточке проекта", blank=True, max_length=200
    )

    skip_sections = models.BooleanField(
        verbose_name="Пропустить секции", default=False, help_text="Отключение секций на генплане"
    )
    disable_parking = models.BooleanField(
        verbose_name="Отключение паркинга",
        default=False,
        help_text="Отключение выбора на генплане и в подборщике",
    )
    status = models.CharField(
        "Статус",
        choices=ProjectStatusType.choices,
        default=ProjectStatusType.CURRENT,
        max_length=20,
    )

    seo_title = models.TextField(verbose_name="SEO заголовок", blank=True)
    seo_description = models.TextField(verbose_name="SEO описание", blank=True)
    seo_keywords = models.TextField(verbose_name="SEO ключевые слова", blank=True)
    cian_id = models.PositiveIntegerField(verbose_name="ID в Cian", null=True, blank=True)
    yandex_id = models.PositiveIntegerField(verbose_name="ID в Yandex", null=True, blank=True)
    highway_cian_id = models.PositiveIntegerField(
        verbose_name="ID шоссе в Cian", null=True, blank=True
    )

    amocrm_name = models.CharField(
        verbose_name="Название в AmoCRM",
        help_text="Для отправки запросов",
        max_length=200,
        blank=True,
    )
    amocrm_enum = models.CharField(
        verbose_name="Enum в AmoCRM", help_text="Для отправки запросов", max_length=200, blank=True
    )
    amocrm_organization = models.CharField(
        verbose_name="Организация в AmoCRM", max_length=200, null=True, blank=True
    )

    latitude = models.DecimalField(
        verbose_name="Широта", decimal_places=6, max_digits=9, null=True, blank=True
    )
    longitude = models.DecimalField(
        verbose_name="Долгота", decimal_places=6, max_digits=9, null=True, blank=True
    )

    video = models.URLField(verbose_name="Видео о проекте", blank=True)
    video_preview = models.ImageField(
        verbose_name="Превью видео", upload_to="p/video_preview", blank=True, null=True
    )
    video_duration = models.CharField(
        verbose_name="Длительность видео", max_length=30, default="2:30"
    )
    presentation = models.FileField(
        verbose_name="Презентация проекта", blank=True, upload_to="p/presentation"
    )

    panorama_title = models.CharField(
        verbose_name="Заголовок для панорамы", max_length=200, blank=True
    )
    panorama_text = models.CharField(verbose_name="Текст для панорамы", max_length=200, blank=True)
    panorama_link = models.URLField(verbose_name="Ссылка для панорамы", blank=True)

    panorama_image = AjaxImageField(
        verbose_name="Изображение панорамы", upload_to="p/panorama", null=True, blank=True
    )

    about_text = models.CharField(
        verbose_name="Текст о проекте", max_length=300, null=True, blank=True
    )
    about_text_colored = models.CharField(
        verbose_name="Выделенный тексто проекте", max_length=300, null=True, blank=True
    )
    about_image = models.ImageField(
        verbose_name="Изображение о проекте", upload_to="p/about_image", blank=True, null=True
    )

    about_furniture = models.FileField(
        verbose_name="О мебели", upload_to="p/about_pdf", blank=True, null=True
    )

    about_furnish = models.FileField(
        verbose_name="Об обтделке", upload_to="p/about_pdf", blank=True, null=True
    )

    about_kitchen = models.FileField(
        verbose_name="О кухне", upload_to="p/about_pdf", blank=True, null=True
    )

    card_image = models.ImageField(
        verbose_name="Изображение на карточке", upload_to="p/card_image", blank=True, null=True
    )
    card_image_night = models.ImageField(
        verbose_name="Изображение на карточке (ночь)",
        upload_to="p/card_image_night",
        blank=True,
        null=True,
    )

    plan = models.ImageField(
        verbose_name="Генплан",
        upload_to="p/p/p1",
        blank=True,
        validators=(FileExtensionValidator(("jpg", "jpeg")),),
        width_field="plan_width",
        height_field="plan_height",
    )
    plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина генплана", null=True, blank=True
    )
    plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота генплана", null=True, blank=True
    )

    ten_minutes_circle = models.ImageField(
        verbose_name="Десятиминутный круг", upload_to="p/p/tmc", null=True, blank=True
    )
    news_title = models.CharField(
        verbose_name="Заголовок новостей", max_length=100, null=True, blank=True
    )
    news_image = models.ImageField(
        verbose_name="Изображение новостей", upload_to="p/p/ni", null=True, blank=True
    )
    socials_title = models.CharField(
        verbose_name="Заголовок соцсетей", max_length=100, null=True, blank=True
    )
    amo_pipeline_id = models.CharField(
        verbose_name="ID  воронки CRM", max_length=20, null=True, blank=True
    )
    amo_responsible_user_id = models.CharField(
        verbose_name="ID  ответственного CRM", max_length=20, null=True, blank=True
    )

    min_flat_price = models.BigIntegerField(verbose_name="Мин цена квартиры", null=True, blank=True)
    min_commercial_prop_price = models.BigIntegerField(
        verbose_name="Мин цена коммерции", null=True, blank=True
    )
    min_commercial_tenant_price = models.BigIntegerField(
        verbose_name="Мин цена арендатор", null=True, blank=True
    )
    min_commercial_business_price = models.BigIntegerField(
        verbose_name="Мин цена бизнес", null=True, blank=True
    )
    min_flat_area = models.DecimalField(
        verbose_name="Мин площадь квартиры", max_digits=7, decimal_places=2, null=True, blank=True
    )
    max_flat_area = models.DecimalField(
        verbose_name="Макс площадь квартиры", max_digits=7, decimal_places=2, null=True, blank=True
    )
    min_commercial_prop_area = models.DecimalField(
        verbose_name="Мин площадь коммерции", max_digits=7, decimal_places=2, null=True, blank=True
    )
    max_commercial_prop_area = models.DecimalField(
        verbose_name="Макс площадь коммерции", max_digits=7, decimal_places=2, null=True, blank=True
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
    min_rate_offers = models.FloatField(
        verbose_name="Мин ставка ипотечного предложения", null=True, blank=True
    )
    min_flat_mortgage = models.BigIntegerField(
        verbose_name="Мин платеж по ипотеке квартир", null=True, blank=True
    )
    min_commercial_mortgage = models.BigIntegerField(
        verbose_name="Мин платеж по ипотеке коммерции", null=True, blank=True
    )
    bank_logo_1 = models.FileField(
        verbose_name="Лого банка 1", upload_to="bank/logo", null=True, blank=True
    )
    bank_logo_2 = models.FileField(
        verbose_name="Лого банка 2", upload_to="bank/logo", null=True, blank=True
    )

    city = models.ForeignKey(
        verbose_name="Город", to="cities.City", on_delete=models.CASCADE, null=True, blank=True
    )
    metro = models.ForeignKey(
        verbose_name="Станция метро", to=Metro, on_delete=models.SET_NULL, blank=True, null=True
    )
    transport = models.ForeignKey(
        verbose_name="Способ передвижения",
        to=Transport,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    ideology = models.ForeignKey(
        verbose_name="Идеология",
        to=ProjectIdeology,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    furnish_title = models.CharField(
        verbose_name="Заголовок для Отделки", max_length=200, blank=True
    )
    is_furnish = models.BooleanField(verbose_name="Отделка", default=True)

    furnish_set = models.ManyToManyField(
        verbose_name="Варианты отделки", to="properties.Furnish", blank=True
    )

    is_furnish_kitchen = models.BooleanField(verbose_name="Отделка кухни", default=False)

    furnish_kitchen_set = models.ManyToManyField(
        verbose_name="Варианты отделки кухни", to="properties.FurnishKitchen", blank=True
    )

    is_furnish_furniture = models.BooleanField(verbose_name="Отделка мебели", default=False)

    furnish_furniture_set = models.ManyToManyField(
        verbose_name="Варианты отделки мебели", to="properties.FurnishFurniture", blank=True
    )

    timer = models.ForeignKey(
        verbose_name="Таймер",
        to="projects.ProjectTimer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Отобразится баннер в футере",
    )
    apartments = models.BooleanField(
        "Проект с апартаментами", default=False, help_text="Меняет название объектов на апартаменты"
    )
    financing_logo = models.ImageField(
        "Логотип финансирования", upload_to="p/p/fi", null=True, blank=True
    )
    display_news_admin = models.BooleanField(
        verbose_name="Выводить в список для новостей/акций", default=True, help_text="В админке"
    )
    label_with_completion = models.CharField(
        verbose_name="Лейбл с ближайшей датой сдачи",
        blank=True,
        null=True,
        max_length=64,
        help_text="Для фильтр квартир, высчитывается автоматически",
    )
    auto_update_label = models.BooleanField(verbose_name="Aвтообновление лейбла", default=True)
    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)
    close_sync = models.BooleanField(
        verbose_name="Скрыть для синхронизации с ProfitBase", default=False
    )
    logo = AjaxImageField(
        "Логотип",
        upload_to="p/p/logo",
        null=True,
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )
    show_close = models.BooleanField("Отображать в фильтре квартир 'ближ.'", default=True)

    # panel manager
    show_in_panel_manager = models.BooleanField("Показывать в панеле мендежера", default=True)
    image_panel_manager = models.ImageField(
        "Изображение на главном экране", upload_to="p/p/ipm", blank=True, null=True
    )

    dont_commercial_prop_update = models.BooleanField(
        "Не обновлять площади коммерции", default=False
    )
    open_booking_with_sale = models.BooleanField(
        "Открыть бронирование для квартир со скидкой", default=False
    )

    # для Движ.API
    dvizh_id = models.PositiveIntegerField(
        verbose_name="id комплекса в Движ.API", null=True, blank=True
    )
    dvizh_uuid = models.CharField(
        verbose_name="UUID комплекса в Движ.API",
        null=True,
        blank=True,
        editable=False,
        max_length=120,
    )

    polygon_in_map = models.TextField(verbose_name="Обводка на карте", blank=True)

    mini_map = AjaxImageField(
        "Мини-карта",
        upload_to="p/p/map",
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )

    # Шаблоны для безнесс-класса
    is_single_building = models.BooleanField(
        "Проект только с одним зданием", default=False,
        help_text="используется для разметки секций на генплане ЖК"
    )
    header_text = models.CharField(verbose_name="Текст в шапке", max_length=200, blank=True)
    header_title = models.CharField(verbose_name="Заголовок в шапке", max_length=200, blank=True)
    header_image = models.ImageField(
        "Логотип в шапке", upload_to="p/p/fi", null=True, blank=True
    )
    # Видеоэкскурсия
    business_video_tour_title = models.CharField(verbose_name="Заголовок в блоке 'Видеоэкскурсия'", max_length=200, blank=True)
    business_video_tour_text = models.CharField(verbose_name="Текст в блоке 'Видеоэкскурсия'", max_length=200, blank=True)
    business_video_tour_image = models.ImageField(
        "Картинка в блоке 'Видеоэкскурсия'", upload_to="p/p/fi", null=True, blank=True
    )

    ## Кладовые и паркинг

    business_pantry_title = models.CharField(verbose_name="Заголовок блока Кладовые", max_length=200, blank=True)
    business_pantry_desc = models.TextField(verbose_name="Описание блока Кладовые", blank=True)
    business_pantry_count = models.PositiveIntegerField(verbose_name="Количество кладовых", default=0)
    business_pantry_img = models.ImageField(
        "Изображение блока Кладовые", upload_to="p/p/bus", blank=True, null=True
    )

    business_parking_title = models.CharField(verbose_name="Заголовок блока Паркинг", max_length=200, blank=True)
    business_parking_desc = models.TextField(verbose_name="Описание блока Паркинг", blank=True)
    business_parking_count = models.PositiveIntegerField(verbose_name="Количество паркинга", default=0)
    business_parking_img = models.ImageField(
        "Изображение блока Паркинг", upload_to="p/p/bus", blank=True, null=True
    )

    ## Выбор за вами

    business_choice_title = models.CharField(verbose_name="Заголовок блока 'Выбор за вами'", max_length=200, blank=True)
    business_choice_desc = models.TextField(verbose_name="Описание блока 'Выбор за вами'", blank=True)
    business_choice_img = models.ImageField(
        "Изображение блока 'Выбор за вами'", upload_to="p/p/bus", blank=True, null=True
    )

    business_flats_title = models.CharField(verbose_name="Заголовок блока Квартиры", max_length=200, blank=True)
    business_special_offers_title = models.CharField(verbose_name="Заголовок блока Акции", max_length=200, blank=True)
    business_purchase_methods_title = models.CharField(verbose_name="Заголовок блока Способы покупки",
                                                       max_length=200, blank=True)

    business_office_title = models.CharField(verbose_name="Заголовок блока Офисы продаж", max_length=200, blank=True)
    business_benefits_title = models.CharField(verbose_name="Заголовок блока Преимущества", max_length=200, blank=True)

    image_map = {
        "image_display": Spec(source="image", default="png", width=1462, height=1406),
        "image_preview": Spec(source="image", default="png", width=731, height=703, blur=True),
        "image_display_pin": Spec(source="image", default="png", width=50, height=50),
        "image_preview_pin": Spec(source="image", default="png", width=50, height=50, blur=True),
        "panorama_image_display": Spec(source="panorama_image", width=1328, height=440),
        "panorama_image_preview": Spec(source="panorama_image", width=1328, height=440, blur=True),
        "card_image_display": Spec(source="card_image", width=962, height=496),
        "card_image_preview": Spec(source="card_image", width=481, height=249, blur=True),
        "card_image_night_display": Spec(source="card_image_night", width=962, height=496),
        "card_image_night_preview": Spec(
            source="card_image_night", width=481, height=249, blur=True
        ),
        "about_image_display": Spec(source="about_image", width=1456, height=1402),
        "about_image_preview": Spec(source="about_image", width=728, height=701, blur=True),
        "plan_display": Spec(source="plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT),
        "plan_preview": Spec(
            source="plan",
            width=int(PLAN_DISPLAY_WIDTH / 2),
            height=int(PLAN_DISPLAY_HEIGHT / 2),
            blur=True,
        ),
        "image_panel_manager_display": Spec(
            source="image_panel_manager", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT
        ),
        "image_panel_manager_preview": Spec(
            source="image_panel_manager",
            width=int(PLAN_DISPLAY_WIDTH / 2),
            height=int(PLAN_DISPLAY_HEIGHT / 2),
            blur=True,
        ),
        "plan_light_display": Spec(source="plan", width=2000, height=1250),
        "plan_light_preview": Spec(source="plan", width=1000, height=625, blur=True),
        "financing_logo_display": Spec(source="financing_logo", width=488, height=140),
        "financing_logo_preview": Spec(source="financing_logo", width=488, height=140, blur=True),
        "parking_image_display": Spec(source="parking_image", width=1456, height=1402),
        "parking_image_preview": Spec(source="parking_image", width=728, height=701, blur=True),
        "video_preview_display": Spec(source="video_preview", width=488, height=140),
        "video_preview_preview": Spec(source="video_preview", width=488, height=140, blur=True),
    }

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.button_is_redirect:
            if not self.button_link:
                raise ValidationError({"button_link": "Неопределено поле"})
            if not self.button_name:
                raise ValidationError({"button_name": "Неопределено поле"})
        if self.is_redirect:
            if not self.redirect_link:
                raise ValidationError({"redirect_link": "Неопределено поле"})

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ("order",)

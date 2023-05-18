from ajaximage.fields import AjaxImageField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import F, Q, UniqueConstraint
from django.db.models.functions import Abs
from graphql_relay import to_global_id

from common.fields import PolygonField

from ..constants import PropertyStatus, PropertyType
from ..querysets import PropertyQuerySet
from ..tasks import convert_to_png


class Property(models.Model):
    """
    Объект собственности
    """

    objects = PropertyQuerySet.as_manager()

    number = models.CharField(verbose_name="Номер", max_length=100, blank=True, db_index=True)
    article = models.CharField(verbose_name="Артикул", max_length=100, blank=True, db_index=True)
    price = models.DecimalField(
        verbose_name="Цена", max_digits=14, decimal_places=2, db_index=True, default=0
    )
    hide_price = models.BooleanField(verbose_name="Скрыть цену", default=False)
    area = models.DecimalField(
        verbose_name="Площадь", max_digits=8, decimal_places=2, db_index=True
    )
    promo_start = models.DateTimeField(
        verbose_name="Начало скидки", null=True, blank=True, db_index=True
    )
    promo_end = models.DateTimeField(
        verbose_name="Конец скидки", null=True, blank=True, db_index=True
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    changed = models.DateTimeField(verbose_name="Изменено", auto_now=True, db_index=True)
    hash = models.BinaryField(verbose_name="Хэш", max_length=20, null=True, blank=True)
    rooms = models.PositiveSmallIntegerField(
        verbose_name="Комнатность", db_index=True, null=True, blank=True
    )
    number_on_floor = models.PositiveSmallIntegerField(
        verbose_name="Номер на этаже", null=True, blank=True
    )
    is_bathroom_window = models.BooleanField(verbose_name='Окно в ванной', default=False)
    is_cityhouse = models.BooleanField(verbose_name='Ситихаус', default=False)
    is_apartments = models.BooleanField(verbose_name="Апартаменты", default=False)
    is_penthouse = models.BooleanField(verbose_name="Пентхаус", default=False)
    is_angular = models.BooleanField(verbose_name="Квартира угловая", default=False)
    is_auction = models.BooleanField(verbose_name="Участвует в аукционе", default=False)
    is_pantry = models.BooleanField(verbose_name="Кладовка", default=False)
    open_plan = models.BooleanField(verbose_name="Свободная планировка", default=False)
    facing = models.BooleanField(verbose_name="Отделка", default=False)
    has_view = models.BooleanField(verbose_name="Видовая", default=False)
    installment = models.BooleanField(verbose_name="Рассрочка", default=False, db_index=True)
    frontage = models.BooleanField(verbose_name="Палисадник", default=False)
    preferential_mortgage = models.BooleanField(
        "Льготная ипотека",
        default=False,
        db_index=True,
        help_text="Если true, онлайн-бронирование отключено, на странице лота появляется форма дефолтного бронирования.",
    )
    preferential_mortgage4 = models.BooleanField(
        "Льготная ипотека 4.95%", default=False, db_index=True
    )
    corner_windows = models.BooleanField(verbose_name="Угловые окна", default=False)
    maternal_capital = models.BooleanField(verbose_name="Материнский капитал", default=False)

    type = models.CharField(
        verbose_name="Тип", max_length=20, db_index=True, choices=PropertyType.choices
    )
    status = models.PositiveSmallIntegerField(
        verbose_name="Статус",
        default=PropertyStatus.FREE,
        choices=PropertyStatus.choices,
        db_index=True,
    )

    original_price = models.DecimalField(
        verbose_name="Оригинальная цена",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    furnish_price_per_meter = models.DecimalField(
        verbose_name="Цена с отделкой за метр",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    furnish_comfort_price_per_meter = models.DecimalField(
        verbose_name="Цена с отделкой комфорт за метр",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )

    furnish_business_price_per_meter = models.DecimalField(
        verbose_name="Цена с отделкой бизнес за метр",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    is_kitchen = models.BooleanField(verbose_name='Кухня (для фильтра)', default=False)

    kitchen_price = models.DecimalField(
        verbose_name="Цена кухни",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    is_furniture = models.BooleanField(verbose_name='Мебель (для фильтра)', default=False)

    furniture_price = models.DecimalField(
        verbose_name="Цена мебелировки",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )

    price_per_meter = models.DecimalField(
        verbose_name="Цена за квадратный метр",
        max_digits=14,
        decimal_places=2,
        db_index=True,
        null=True,
        blank=True,
    )

    bedrooms_count = models.PositiveSmallIntegerField(
        verbose_name="Количество спален", null=True, blank=True
    )
    loggias_count = models.PositiveSmallIntegerField(
        verbose_name="Количество лоджей", null=True, blank=True
    )
    balconies_count = models.PositiveSmallIntegerField(
        verbose_name="Количество балконов", null=True, blank=True
    )
    stores_count = models.PositiveSmallIntegerField(
        verbose_name="Количество кладовых", null=True, blank=True
    )
    living_area = models.DecimalField(
        verbose_name="Площадь", max_digits=8, decimal_places=2, null=True, blank=True
    )
    kitchen_area = models.DecimalField(
        verbose_name="Площадь кухни", max_digits=8, decimal_places=2, null=True, blank=True
    )

    no_balcony_and_terrace_area = models.DecimalField(
        verbose_name="Площадь без балкона и террасы", default=0.00, max_digits=8, decimal_places=2, blank=True
    )

    wardrobes_count = models.PositiveSmallIntegerField(
        verbose_name="Количество гардеробных", null=True, blank=True
    )
    separate_wcs_count = models.PositiveSmallIntegerField(
        verbose_name="Количество раздельных санузлов", null=True, blank=True
    )
    combined_wcs_count = models.PositiveSmallIntegerField(
        verbose_name="Количество совмещённых санузлов", null=True, blank=True
    )

    plan = AjaxImageField(
        verbose_name="Планировка",
        upload_to="pp/f/p",
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )
    commercial_plan = AjaxImageField(
        verbose_name="Планировка апартаментов коммерции",
        upload_to="pp/f/p",
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
        help_text="Для фильтра коммерции",
    )
    plan_png = models.FileField(
        "Планировка в PNG", upload_to="pp/f/pp", blank=True, help_text="Генерируется автоматически"
    )
    plan_png_preview = models.FileField(
        "Планировка в PNG - превью на карточке",
        upload_to="pp/f/ppp",
        blank=True,
        help_text="Генерируется автоматически",
    )
    plan_3d = models.ImageField(
        "Планировка 3d", upload_to="pp/i/p3", blank=True, help_text="Добавляется вручную"
    )
    plan_3d_1 = models.ImageField(
        "3D-планировка", upload_to="pp/i/p3", blank=True, help_text="Добавляется вручную"
    )

    plan_hover = PolygonField(verbose_name="Обводка на плане", source="floor.plan", blank=True)
    plan_code = models.CharField(verbose_name="Код планировки", max_length=100, blank=True)

    parking = models.CharField(verbose_name='Номер паркинга', max_length=200, blank=True, null=True)
    has_parking = models.BooleanField(verbose_name="Парковка", default=False)
    has_action_parking = models.BooleanField(verbose_name="Паркинг по спец. цене", default=False)
    has_terrace = models.BooleanField(verbose_name="Терраса", default=False)
    is_duplex = models.BooleanField(verbose_name="Двухуровневая", default=False)
    has_high_ceiling = models.BooleanField(verbose_name="Высокий потолок", default=False)
    has_panoramic_windows = models.BooleanField(verbose_name="Панорамные окна", default=False)
    has_two_sides_windows = models.BooleanField(verbose_name="Окна на 2 стороны", default=False)
    has_tenant = models.BooleanField(verbose_name="С арендатором", default=False)
    for_business = models.BooleanField(verbose_name="Для бизнеса", default=False)
    favorable_rate = models.BooleanField(verbose_name="Выгодная ставка", default=False)
    kitchen_living = models.BooleanField(verbose_name="Кухня-гостинная", null=True, blank=True)
    lounge_balcony = models.BooleanField(verbose_name="Лаунж-балкон", null=True, blank=True)
    has_separate_entrance = models.BooleanField(
        verbose_name="Отдельная входная группа", default=False
    )
    has_two_entrances = models.BooleanField(verbose_name="Два входа", default=False)
    has_stained_glass = models.BooleanField(verbose_name="Витражное остекление", default=False)
    has_functional_layout = models.BooleanField(
        verbose_name="Функциональная планировка", default=False
    )
    has_place_for_ads = models.BooleanField(verbose_name="Место под рекл. вывеску", default=False)
    has_ceiling_three_meters = models.BooleanField(verbose_name="Потолок 3-3,6м", default=False)
    has_water_supply = models.BooleanField(
        verbose_name="Горячее и холодное водоснабжение", default=False
    )
    has_dot_two_kilowatts = models.BooleanField(
        verbose_name="Эл. мощность 0,2 кВт/м2", default=False
    )
    has_own_ventilation = models.BooleanField(verbose_name="Собственная вент. шахта", default=False)
    view_cathedral = models.BooleanField(verbose_name="Вид на Исаакиевский собор", default=False)
    view_gulf = models.BooleanField(verbose_name="Вид на Финский залив", default=False)
    view_river = models.BooleanField(verbose_name="Вид на реку", default=False)
    view_park = models.BooleanField(verbose_name="Вид на парк Екатерингоф", default=False)
    view_temple = models.BooleanField(verbose_name="Вид на храм", default=False)
    view_square = models.BooleanField(verbose_name="Вид на сквер", default=False)
    view_center = models.BooleanField(verbose_name="Вид на центр", default=False)
    developed_infrastructure = models.BooleanField(
        verbose_name="Развитая инфраструктура", default=False
    )
    first_line = models.BooleanField(verbose_name="Первая линия", default=False)
    renovate = models.BooleanField(verbose_name="Ремонт", default=False)
    master_bedroom = models.BooleanField(verbose_name="Мастер-спальня", default=False)
    design_gift = models.BooleanField(verbose_name="Дизайн-проект в подарок", default=False)
    is_euro_layout = models.BooleanField(verbose_name="Европланировка", default=False)
    smart_house = models.BooleanField(verbose_name="Умный дом", default=False)

    facade = models.CharField(verbose_name="Фасады", max_length=50, null=True, blank=True)
    yards = models.CharField(verbose_name="Дворы", max_length=50, null=True, blank=True)
    security = models.CharField(verbose_name="Безопасность", max_length=50, null=True, blank=True)
    storage = models.CharField(verbose_name="Кладовая", max_length=50, null=True, blank=True)
    action = models.CharField(verbose_name="Акция", max_length=50, null=True, blank=True)
    planoplan = models.TextField(verbose_name="URL для виджета от Planoplan", blank=True)
    is_planoplan = models.BooleanField(verbose_name="Виджет от Planoplan", default=False)
    planoplan_commercial = models.TextField(
        verbose_name="URL для виджета от Planoplan (коммерческий апартамент)", blank=True
    )
    bathroom_area = models.DecimalField(
        verbose_name="Площадь санузла", max_digits=8, decimal_places=2, null=True, blank=True
    )

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    building = models.ForeignKey(
        verbose_name="Корпус",
        to="buildings.Building",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    section = models.ForeignKey(
        to="buildings.Section",
        verbose_name="Секция",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    floor = models.ForeignKey(
        verbose_name="Этаж", to="buildings.Floor", on_delete=models.CASCADE, null=True, blank=True
    )
    furnish_set = models.ManyToManyField(
        verbose_name="Варианты отделки", to="properties.Furnish", blank=True
    )
    furnish_kitchen_set = models.ManyToManyField(
        verbose_name="Варианты отделки кухни", to="properties.FurnishKitchen", blank=True
    )

    furnish_furniture_set = models.ManyToManyField(
        verbose_name="Варианты отделки мебели", to="properties.FurnishFurniture", blank=True
    )
    purposes = models.ManyToManyField(
        verbose_name="Назначения помещения", to="properties.PropertyPurpose", blank=True
    )
    window_view = models.ForeignKey(
        verbose_name="Вид из окна",
        to="properties.WindowView",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    mini_plan_point = models.ForeignKey(
        verbose_name="Точка на миниплане",
        to="properties.MiniPlanPoint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    layout = models.ForeignKey(
        verbose_name="Планировка",
        to="properties.Layout",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    views_count = models.IntegerField(
        verbose_name="Количество просмотров", default=0, db_index=True
    )
    hypo_popular = models.BooleanField("Популярная(для гипотезы)", default=False)
    hypo_min_mortgage = models.IntegerField(
        verbose_name="Ежемесячный платеж(для гипотезы)", null=True, editable=False
    )
    map_hover = models.TextField(verbose_name="Обводка на карте", blank=True)
    profitbase_id = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="ID в Profitbase", help_text="внутренний ID объекта собственности в Profitbase"
    )

    # debug
    update_text = models.TextField("Отладка обновления", blank=True)
    update_time = models.DateTimeField("Дата последнего обновления", blank=True, null=True)

    def __str__(self) -> str:
        str_ = f"{self._meta.verbose_name} #{self.id}"
        if self.article:
            str_ += f" #{self.article}"
        return str_

    @property
    def similar_flats(self) -> PropertyQuerySet:
        return (
            Property.objects.filter_similar_flats(self)
            .annotate(price_diff=Abs(F("price") - self.price))
            .order_by("price_diff")
        )

    @property
    def similar_commercial_spaces(self) -> PropertyQuerySet:
        return (
            Property.objects.filter_similar_commercial_spaces(self)
            .annotate(price_diff=Abs(F("price") - self.price))
            .order_by("price_diff")
        )

    def get_url(self):
        domain = "strana.com"
        if self.project.city:
            domain = self.project.city.site.domain
        property_ids = to_global_id("GlobalFlatType", self.id)
        return f"https://{domain}/{self.project.slug}/flats/{property_ids}/"

    class Meta:
        verbose_name = "Объект собственности"
        verbose_name_plural = "Объекты собственности"
        ordering = ("id",)
        constraints = (
            UniqueConstraint(
                fields=("building", "number", "id"),
                name="unique_property_building_number",
                condition=Q(number__isnull=False),
            ),
        )

    def convert_plan_to_png(self):
        if self.plan:
            convert_to_png.delay(
                app_label="properties",
                model="property",
                pk=self.id,
                to_attr="plan_png",
                url=self.plan.url,
                width=1900,
                height=1400,
            )
            convert_to_png.delay(
                app_label="properties",
                model="property",
                pk=self.id,
                to_attr="plan_png_preview",
                url=self.plan.url,
                width=900,
                height=700,
            )

    def save(self, *args, **kwargs):
        from .layout import Layout
        super().save(*args, **kwargs)
        if self.furnish_kitchen_set and self.building and self.kitchen_price:
            if self.building.show_furnish_kitchen:
                self.is_kitchen = True

        if self.furnish_furniture_set and self.building and self.furniture_price:
            if self.building.show_furnish_furniture:
                self.is_furniture = True

        if self.planoplan:
            self.is_planoplan = True
        if not self.plan and self.layout:
            if layout_obj := Layout.objects.filter(pk=self.layout.id).first():
                if plan_url := layout_obj.plan.name:
                    self.plan.name = plan_url
        # if not self.plan and self.project and self.building and self.number:
        #     path_to_file = f'/bim/{self.project.slug}/{self.building.name}/{self.number}.svg'
        #     self.plan.name = path_to_file
        if (not self.plan_hover or self.plan_hover == ['']) and self.layout:
            if layout_obj := Layout.objects.filter(pk=self.layout.id).first():
                self.plan_hover = layout_obj.plan_hover
        super().save()

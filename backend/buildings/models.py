import re
import zipfile

from ajaximage.fields import AjaxImageField
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import (FileExtensionValidator, MaxValueValidator,
                                    MinValueValidator)
from django.db import models

from django.conf import settings
from common.fields import PolygonField, PpoiField
from common.models import MultiImageMeta, Spec

from .constants import BuildingType
from .querysets import BuildingQuerySet, FloorQuerySet, SectionQuerySet


class Building(models.Model, metaclass=MultiImageMeta):
    """
    Корпус
    """

    PLAN_DISPLAY_WIDTH = 2880
    PLAN_DISPLAY_HEIGHT = 1800

    STATE_BUILT = "built"
    STATE_READY = "ready"
    STATE_HAND_OVER = "hand_over"
    STATE_UNFINISHED = "unfinished"

    STATE_CHOICES = (
        (STATE_UNFINISHED, "Cтроится"),
        (STATE_BUILT, "Построен, но не сдан"),
        (STATE_READY, "Построен и сдан"),
        (STATE_HAND_OVER, "Сдан в эксплуатацию"),
    )

    TYPE_PANEL = "panel"
    TYPE_BRICK = "brick"
    TYPE_MONOLITHIC = "monolithic"
    TYPE_BRICK_MONOLITHIC = "brick_monolithic"
    TYPE_FRAME_MONOLITHIC = "frame_monolithic"

    TYPE_CHOICES = (
        (TYPE_PANEL, "Панельный"),
        (TYPE_MONOLITHIC, "Монолитный"),
        (TYPE_BRICK, "Кирпичный"),
        (TYPE_BRICK_MONOLITHIC, "Кирпично-монолитный"),
        (TYPE_FRAME_MONOLITHIC, "Монолитно-каркасный"),
    )

    objects = BuildingQuerySet.as_manager()

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    panorama_yard_link = models.URLField(verbose_name="Ссылка для панорамы двора", blank=True)

    panorama_front_door_link = models.URLField(verbose_name="Ссылка для панорамы парадной", blank=True)

    presentation_link = models.URLField(verbose_name="Ссылка для презентации", blank=True)

    street = models.CharField(verbose_name="Улица", max_length=100, blank=True)
    address = models.CharField(verbose_name="Адрес", max_length=300, null=True, blank=True)

    name = models.CharField(verbose_name="Название", max_length=50, db_index=True)
    is_active = models.BooleanField("Активен", default=True)
    panorama_file = models.FileField(
        verbose_name="файл с архивом панорамы", null=True, blank=True, upload_to='b/p/p/',
    )
    panorama_url = models.TextField(
        verbose_name="URL на файл с панорамой",
        help_text="устанавливается автоматически после распаковки и загрузки архива",
        blank=True
    )
    number = models.CharField(verbose_name="Номер", max_length=50, blank=True, db_index=True)
    building_state = models.CharField(
        verbose_name="Состояние", max_length=20, choices=STATE_CHOICES
    )
    building_type = models.CharField(
        verbose_name="Тип", max_length=20, choices=TYPE_CHOICES, blank=True
    )
    residential_set = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        limit_choices_to={"kind": BuildingType.RESIDENTIAL},
        verbose_name="Жилое строение",
        help_text="Привязывает коммерческие к жилым помещениям",
    )

    show_furnish = models.BooleanField("Показывать отделки", default=False)

    furnish_set = models.ManyToManyField(
        verbose_name="Варианты отделки", to="properties.Furnish", blank=True
    )

    show_furnish_kitchen = models.BooleanField("Показывать отделки кухни", default=False)

    furnish_kitchen_set = models.ManyToManyField(
        verbose_name="Варианты отделки кухни", to="properties.FurnishKitchen", blank=True
    )

    show_furnish_furniture = models.BooleanField("Показывать отделки мебели", default=False)

    furnish_furniture_set = models.ManyToManyField(
        verbose_name="Варианты отделки мебели", to="properties.FurnishFurniture", blank=True
    )

    building_phase = models.PositiveIntegerField(
        verbose_name="Очередь строительства", null=True, blank=True
    )

    name_display = models.CharField(
        verbose_name="Отображаемое имя", max_length=100, null=True, blank=True
    )

    kind = models.CharField(
        verbose_name="Тип строения",
        max_length=32,
        choices=BuildingType.choices,
        default=BuildingType.RESIDENTIAL,
        db_index=True,
    )
    ceiling_height = models.DecimalField(
        verbose_name="Высота потолков", decimal_places=2, max_digits=4, null=True, blank=True
    )
    passenger_lifts_count = models.PositiveIntegerField(
        verbose_name="Количество пассажирских лифтов", null=True, blank=True
    )
    cargo_lifts_count = models.PositiveIntegerField(
        verbose_name="Количество грузовых лифтов", null=True, blank=True
    )
    compass_azimuth = models.PositiveSmallIntegerField(
        verbose_name="Градус компаса",
        validators=(MinValueValidator(0), MaxValueValidator(360)),
        default=180,
    )
    compass_street_top = models.CharField(
        verbose_name="Верхняя улица на компасе", max_length=100, null=True, blank=True
    )
    compass_street_bottom = models.CharField(
        verbose_name="Нижняя улица на компасе", max_length=100, null=True, blank=True
    )
    compass_street_left = models.CharField(
        verbose_name="Левая улица на компасе", max_length=100, null=True, blank=True
    )
    compass_street_right = models.CharField(
        verbose_name="Правая улица на компасе", max_length=100, null=True, blank=True
    )
    sun_azimuth = models.PositiveSmallIntegerField(
        verbose_name="Градус солнца",
        validators=(MinValueValidator(0), MaxValueValidator(360)),
        default=180,
    )
    start_date = models.DateField(verbose_name="Дата старта строительства", blank=True, null=True)
    finish_date = models.DateField(
        verbose_name="Дата окончания строительства", blank=True, null=True
    )
    fact_date = models.DateField(verbose_name="Дата сдачи по факту", blank=True, null=True)
    current_level = models.PositiveSmallIntegerField(
        verbose_name="Текущий уровень готовности",
        validators=(MinValueValidator(0), MaxValueValidator(100)),
        default=0,
        help_text='Высчитывается автоматически по полям "Дата старта строительства" и "Дата сдачи по факту"',
    )
    built_year = models.PositiveIntegerField(
        verbose_name="Год сдачи",
        null=True,
        blank=True,
        validators=(MinValueValidator(1900), MaxValueValidator(2100)),
        db_index=True,
        help_text='Высчитывается автоматически из поля "Дата окончания строительства"',
    )
    ready_quarter = models.PositiveIntegerField(
        verbose_name="Квартал сдачи",
        null=True,
        blank=True,
        validators=(MinValueValidator(1), MaxValueValidator(4)),
        db_index=True,
        help_text='Высчитывается автоматически из поля "Дата окончания строительства"',
    )

    plan = models.ImageField(
        verbose_name="Планировка",
        upload_to="b/b/p",
        blank=True,
        null=True,
        validators=(FileExtensionValidator(("jpg", "jpeg")),),
        width_field="plan_width",
        height_field="plan_height",
    )
    plan_night = models.ImageField(
        verbose_name="Планировка (ночь)",
        upload_to="b/b/pn",
        blank=True,
        null=True,
        validators=(FileExtensionValidator(("jpg", "jpeg")),),
        width_field="plan_width",
        height_field="plan_height",
    )
    commercial_plan = models.ImageField(
        verbose_name="Планировка коммерции",
        upload_to="b/b/cp",
        blank=True,
        null=True,
        validators=(FileExtensionValidator(("jpg", "jpeg")),),
    )
    plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина планировки", null=True, blank=True
    )
    plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота планировки", null=True, blank=True
    )
    window_view_hypo = models.ImageField(
        verbose_name="Изображение вида из окна (гипотеза)", upload_to="b/b/wvh", blank=True
    )
    window_view_plan = models.ImageField(
        verbose_name="План вида из окна",
        upload_to="b/b/wvp",
        blank=True,
        validators=(FileExtensionValidator(("jpg", "jpeg")),),
        width_field="window_view_plan_width",
        height_field="window_view_plan_height",
    )
    window_view_plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина плана вида из окна", null=True, blank=True
    )
    window_view_plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота плана вида из окна", null=True, blank=True
    )
    mini_plan = models.ImageField(
        verbose_name="Мини-планировка",
        upload_to="b/b/mp",
        blank=True,
        null=True,
        validators=(FileExtensionValidator(("jpg", "jpeg", "png")),),
        width_field="mini_plan_width",
        height_field="mini_plan_height",
    )
    mini_plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина мини-планировки", null=True, blank=True
    )
    mini_plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота мини-планировки", null=True, blank=True
    )

    plan_hover = PolygonField(verbose_name="Обводка на генплане", source="project.plan", blank=True)
    point = PpoiField(
        verbose_name="Точка на генплане", source="project.plan", null=True, blank=True
    )
    plan_yard = PolygonField(verbose_name="Обводка дворов и парадной", source="project.plan", blank=True)
    yard_point = PpoiField(
        verbose_name="Точка дворов и парадной", source="project.plan", null=True, blank=True,
        default='0,0'
    )

    cian_id = models.PositiveIntegerField(verbose_name="ID в cian", null=True, blank=True)
    yandex_id = models.PositiveIntegerField(verbose_name="ID в Yandex", null=True, blank=True)
    changed = models.DateTimeField(verbose_name="Изменено", auto_now=True, db_index=True)
    hash = models.BinaryField(verbose_name="Хэш", max_length=20, null=True, blank=True)
    booking_active = models.BooleanField(verbose_name="Бронирование активно", default=True)
    booking_period = models.PositiveSmallIntegerField(
        verbose_name="Длительность бронирования", default=30
    )
    booking_price = models.PositiveIntegerField(verbose_name="Стоимость бронирования", default=5000)
    booking_types = models.ManyToManyField(
        to="buildings.BuildingBookingType", verbose_name="Типы бронирования", blank=True
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

    image_map = {
        "plan_display": Spec(source="plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT),
        "plan_preview": Spec(
            source="plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT, blur=True
        ),
        "plan_night_display": Spec(
            source="plan_night", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT
        ),
        "plan_night_preview": Spec(
            source="plan_night", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT, blur=True
        ),
        "commercial_plan_display": Spec(
            source="commercial_plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT
        ),
        "commercial_plan_preview": Spec(
            source="commercial_plan",
            width=PLAN_DISPLAY_WIDTH,
            height=PLAN_DISPLAY_HEIGHT,
            blur=True,
        ),
        "window_view_plan_display": Spec(
            source="window_view_plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT
        ),
        "window_view_plan_preview": Spec(
            source="window_view_plan",
            width=int(PLAN_DISPLAY_WIDTH / 2),
            height=int(PLAN_DISPLAY_HEIGHT / 2),
            blur=True,
        ),
        "window_view_plan_lot_display": Spec(
            source="window_view_plan",
            width=int(PLAN_DISPLAY_WIDTH / 6),
            height=int(PLAN_DISPLAY_HEIGHT / 6),
        ),
        "window_view_plan_lot_preview": Spec(
            source="window_view_plan",
            width=int(PLAN_DISPLAY_WIDTH / 6),
            height=int(PLAN_DISPLAY_HEIGHT / 6),
            blur=True,
        ),
        "window_view_hypo_display": Spec(
            source="window_view_hypo",
            width=int(PLAN_DISPLAY_WIDTH / 2),
            height=int(PLAN_DISPLAY_HEIGHT / 2),
        ),
        "window_view_hypo_preview": Spec(
            source="window_view_hypo",
            width=int(PLAN_DISPLAY_WIDTH / 2),
            height=int(PLAN_DISPLAY_HEIGHT / 2),
            blur=True,
        ),
    }

    def __str__(self) -> str:
        return f"Корпус {self.name}"

    def clean(self) -> None:
        if not self.name_display:
            raise ValidationError({"name_display": "Отображаемое имя обязательно."})
        if self.panorama_file and not self.panorama_file.closed and not zipfile.is_zipfile(self.panorama_file.file):
            raise ValidationError({"panorama_file": "Файл не является поддерживаемым типом архива."})

    @property
    def get_state_cian(self) -> bool:
        if self.building_state == self.STATE_HAND_OVER:
            return True
        else:
            return False

    @property
    def get_state_yandex(self) -> str:
        return self.building_state.replace("_", "-")

    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпуса"
        unique_together = (("project", "name"),)
        ordering = ("name",)


class BuildingBookingType(models.Model):
    period = models.PositiveSmallIntegerField(verbose_name="Длительность бронирования", default=30)
    price = models.PositiveIntegerField(verbose_name="Стоимость бронирования", default=5000)
    amocrm_id = models.BigIntegerField(verbose_name="Идентификатор АМОЦРМ", null=True)

    class Meta:
        verbose_name = "Тип бронирования у корпусов"
        verbose_name_plural = "Типы бронирований у корпусов"

    def __str__(self):
        return f"Длительность: {self.period}, стоимость:{self.price}"


class GroupSection(models.Model, metaclass=MultiImageMeta):
    """
    Группа секции
    """

    PLAN_DISPLAY_WIDTH = 2880
    PLAN_DISPLAY_HEIGHT = 1800

    building = models.ForeignKey(Building, models.CASCADE, verbose_name="Корпус")

    name = models.CharField("Название группы секции", max_length=200)
    plan = AjaxImageField(
        "Планировка",
        upload_to="b/gs/p",
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )
    plan_night = AjaxImageField(
        "Планировка (ночь)",
        upload_to="b/gs/pn",
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )
    plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина планировки", null=True, blank=True
    )
    plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота планировки", null=True, blank=True
    )
    order = models.PositiveSmallIntegerField("Очередность", default=0)

    image_map = {
        "plan_display": Spec(source="plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT),
        "plan_preview": Spec(
            source="plan", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT, blur=True
        ),
        "plan_night_display": Spec(
            source="plan_night", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT
        ),
        "plan_night_preview": Spec(
            source="plan_night", width=PLAN_DISPLAY_WIDTH, height=PLAN_DISPLAY_HEIGHT, blur=True
        ),
    }

    class Meta:
        verbose_name = "Группа секции"
        verbose_name_plural = "Группы секции"
        ordering = ("order",)

    def __str__(self):
        return self.name


class Section(models.Model):
    """
    Секция
    """

    objects = SectionQuerySet.as_manager()

    building = models.ForeignKey(verbose_name="Корпус", to=Building, on_delete=models.CASCADE)
    group = models.ForeignKey(
        GroupSection, models.SET_NULL, blank=True, null=True, verbose_name="Группа секции"
    )

    name = models.CharField(verbose_name="Название", max_length=50, blank=True)
    number = models.CharField(verbose_name="Номер", max_length=200, db_index=True)
    changed = models.DateTimeField(verbose_name="Изменено", auto_now=True, db_index=True)

    plan = AjaxImageField(
        "Планировка",
        upload_to="b/s/p",
        blank=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )

    point = PpoiField("Точка на плане", source="building.plan", null=True, blank=True)
    commercial_point = PpoiField(
        "Точка на плане коммерции", source="building.commercial_plan", null=True, blank=True
    )
    plan_hover = PolygonField("Обводка на плане", source="building.plan", blank=True)
    mini_plan_hover = PolygonField("Обводка на мини-плане", source="building.mini_plan", blank=True)
    project_plan_hover = PolygonField("Обводка на генплане ЖК", source="building.project.plan", blank=True)
    total_floors = models.PositiveIntegerField(
        verbose_name="Количество этажей"
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

    def __str__(self) -> str:
        return f"Секция {self.name or str(self.number)}"

    class Meta:
        verbose_name = "Секция"
        verbose_name_plural = "Секции"
        unique_together = (("building", "number"),)
        ordering = ("number",)


class Floor(models.Model):
    """
    Этаж
    """

    objects = FloorQuerySet.as_manager()

    section = models.ForeignKey(verbose_name="Секция", to=Section, on_delete=models.CASCADE)

    number = models.IntegerField(verbose_name="Номер", db_index=True)
    changed = models.DateTimeField(verbose_name="Изменено", auto_now=True, db_index=True)

    plan = AjaxImageField(
        verbose_name="Планировка",
        upload_to="b/f/p",
        validators=(FileExtensionValidator(("svg",)),),
        blank=True,
    )
    plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина планировки", null=True, blank=True
    )
    plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота планировки", null=True, blank=True
    )

    point = PpoiField(verbose_name="Точка на плане", source="section.plan", null=True, blank=True)
    plan_hover = PolygonField(verbose_name="Обводка на плане", source="section.plan", blank=True)
    exit_tooltip = models.CharField(verbose_name="Текст подсказки", max_length=150, blank=True)
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

    def __str__(self) -> str:
        return f"Этаж {self.number}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.plan and not settings.TESTING:
            try:
                with default_storage.open(self.plan.name) as plan_file:
                    plan_content = plan_file.read().decode("utf-8")
            except OSError:
                return
            regex = r'viewBox="\d+\.?\d*\s?\d+\.?\d*\s?\d+\.?\d*\s?\d+\.?\d*\s?"'
            view_boxes = re.findall(regex, plan_content)
            if view_boxes:
                view_box = view_boxes[0]
                sizes = view_box[view_box.find('"') + 1: view_box.rfind('"')]
                sizes = sizes.split(" ")
                if len(sizes) == 4:
                    Floor.objects.filter(id=self.id).update(
                        plan_width=int(float(sizes[2])), plan_height=int(float(sizes[3]))
                    )
                    self.refresh_from_db()

    class Meta:
        verbose_name = "Этаж"
        verbose_name_plural = "Этажи"
        unique_together = (("section", "number"),)
        ordering = ("number",)


class FloorExitPlan(models.Model):
    """
    План выхода этажа
    """

    plan_exit = PpoiField(verbose_name="Выход на плане", source="floor.plan", blank=True)
    floor = models.ForeignKey(verbose_name="Этаж", to=Floor, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "План выхода этажа"
        verbose_name_plural = "Планы выхода этажей"

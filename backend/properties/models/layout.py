from ajaximage.fields import AjaxImageField
from django.core.validators import FileExtensionValidator
from django.db import models

from common.fields import PolygonField

from ..constants import PropertyType
from ..querysets import LayoutQuerySet


class Layout(models.Model):
    """Модель планировки"""

    objects = LayoutQuerySet.as_manager()
    name = models.CharField("Название", unique=True, db_index=True, max_length=32)

    window_view = models.ForeignKey(
        verbose_name="Вид из окна",
        to="properties.WindowView",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    floor = models.ForeignKey(
        "buildings.Floor", verbose_name="Этаж", blank=True, null=True, on_delete=models.SET_NULL
    )
    building = models.ForeignKey(
        "buildings.Building",
        verbose_name="Корпус",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    project = models.ForeignKey(
        "projects.Project", verbose_name="Проект", blank=True, null=True, on_delete=models.SET_NULL
    )
    type = models.CharField(
        verbose_name="Тип", max_length=20, blank=True, null=True, choices=PropertyType.choices
    )
    min_price = models.DecimalField(
        verbose_name="Минимальная цена", max_digits=14, decimal_places=2, blank=True, null=True
    )
    max_discount = models.DecimalField(
        verbose_name="Максимальная скидка", max_digits=14, decimal_places=2, blank=True, null=True
    )
    plan_hover = PolygonField(
        verbose_name="Обводка на плане", source="floor.plan", blank=True, null=True
    )
    hypo_experimental_lot = models.BooleanField("Экспериментальный лот", default=False)
    min_mortgage = models.IntegerField(
        verbose_name="Минимальная ставка по ипотеке(при депозите в 20%)", blank=True, null=True
    )
    """
    fields for annotate_property_stats_static
    """
    rooms = models.PositiveSmallIntegerField(
        verbose_name="Комнатность", db_index=True, null=True, blank=True
    )
    plan = AjaxImageField(
        verbose_name="Планировка объекта собственности",
        upload_to="l/f/p",
        blank=True,
        null=True,
        validators=(FileExtensionValidator(("png", "svg")),),
    )
    planoplan = models.TextField(
        verbose_name="URL для виджета от Planoplan", blank=True, null=True, editable=False
    )
    is_planoplan = models.BooleanField(verbose_name="Виджет от Planoplan", default=False)
    area = models.DecimalField(
        verbose_name="Площадь",
        max_digits=8,
        decimal_places=2,
        db_index=True,
        blank=True,
        null=True,
        editable=False,
    )
    min_floor = models.IntegerField(
        verbose_name="Минимальный этаж", db_index=True, blank=True, null=True, editable=False
    )
    max_floor = models.IntegerField(
        verbose_name="Максимальный этаж", db_index=True, blank=True, null=True, editable=False
    )
    flat_count = models.IntegerField(
        verbose_name="Количество квартир", blank=True, null=True, editable=False
    )
    has_view = models.BooleanField(
        verbose_name="Видовая", default=False, editable=False, blank=True, null=True
    )
    has_parking = models.BooleanField(
        verbose_name="Парковка", default=False, editable=False, blank=True, null=True
    )
    has_action_parking = models.BooleanField(
        verbose_name="Паркинг по спец. цене", default=False, editable=False, blank=True, null=True
    )
    has_terrace = models.BooleanField(
        verbose_name="Терраса", default=False, editable=False, blank=True, null=True
    )
    has_high_ceiling = models.BooleanField(
        verbose_name="Высокий потолок", default=False, editable=False, blank=True, null=True
    )
    has_two_sides_windows = models.BooleanField(
        verbose_name="Окна на 2 стороны", default=False, editable=False, blank=True, null=True
    )
    has_panoramic_windows = models.BooleanField(
        verbose_name="Панорамные окна", default=False, editable=False, blank=True, null=True
    )
    is_duplex = models.BooleanField(
        verbose_name="Двухуровневая", default=False, editable=False, blank=True, null=True
    )
    installment = models.BooleanField(
        verbose_name="Рассрочка",
        default=False,
        db_index=True,
        editable=False,
        blank=True,
        null=True,
    )
    facing = models.BooleanField(
        verbose_name="Отделка", default=False, editable=False, blank=True, null=True
    )
    stores_count = models.PositiveSmallIntegerField(
        verbose_name="Количество кладовых", null=True, blank=True
    )
    frontage = models.BooleanField(
        verbose_name="Палисадник", default=False, editable=False, blank=True, null=True
    )
    floor_plan = AjaxImageField(
        verbose_name="Планировка этажа",
        upload_to="l/f/fp",
        validators=(FileExtensionValidator(("svg",)),),
        blank=True,
        null=True,
    )
    floor_plan_width = models.PositiveSmallIntegerField(
        verbose_name="Ширина планировки этажа", null=True, blank=True, editable=False
    )
    floor_plan_height = models.PositiveSmallIntegerField(
        verbose_name="Высота планировки этажа", null=True, blank=True, editable=False
    )
    floor_plan_hover = PolygonField(
        verbose_name="Обводка на плане",
        source="floor.section.plan",
        editable=False,
        blank=True,
        null=True,
    )
    preferential_mortgage4 = models.BooleanField(
        "Льготная ипотека 4.95%",
        default=False,
        db_index=True,
        editable=False,
        blank=True,
        null=True,
    )
    maternal_capital = models.BooleanField(
        verbose_name="Материнский капитал", default=False, editable=False, blank=True, null=True
    )
    hypo_popular = models.BooleanField(
        verbose_name="Популярная(для гипотезы)",
        default=False,
        editable=False,
        blank=True,
        null=True,
    )
    min_rate = models.FloatField(
        verbose_name="Минимальная процентная ставка", blank=True, null=True
    )
    design_gift = models.BooleanField(
        verbose_name="Дизайн-проект в подарок", default=False, null=True
    )
    flat_sold = models.PositiveSmallIntegerField(
        verbose_name="Количество проданных квартир", null=True, blank=True
    )

    class Meta:
        verbose_name = "Планировка"
        verbose_name_plural = "Планировки"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.planoplan:
            self.is_planoplan = True
        super().save(*args, **kwargs)

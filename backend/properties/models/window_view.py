from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from buildings.constants import BuildingType
from common.fields import PpoiField


class WindowViewType(models.Model):
    """ Модель типа вида из окна """

    title = models.CharField(verbose_name="Название типа", max_length=32)
    building = models.ForeignKey(
        verbose_name="Корпус",
        to="buildings.Building",
        on_delete=models.CASCADE,
        limit_choices_to={"kind": BuildingType.RESIDENTIAL},
    )
    section = models.ForeignKey(
        verbose_name="Секция",
        to="buildings.Section",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={"building__kind": BuildingType.RESIDENTIAL},
    )

    class Meta:
        verbose_name = "Тип вида из окна"
        verbose_name_plural = "Тип вида из окна"

    def __str__(self):
        return self.title


class WindowViewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('type')


class WindowView(models.Model):
    """ Модель вида из окна """

    ppoi = PpoiField(verbose_name="Точка на плане", source="type.building.window_view_plan")
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)
    type = models.ForeignKey(
        "properties.WindowViewType", models.CASCADE, verbose_name="Тип вида из окна"
    )
    objects = WindowViewManager()

    class Meta:
        ordering = ("order",)
        verbose_name = "Вид из окна"
        verbose_name_plural = "Виды из окон"

    def __str__(self):
        return f"{self.order}, {self.type}"


class WindowViewAngle(models.Model):
    """ Модель угла обзора из окна """

    angle = models.PositiveSmallIntegerField(
        verbose_name="Угол", validators=[MinValueValidator(1), MaxValueValidator(360)]
    )
    window_view = models.ForeignKey(
        verbose_name="Вид из окна", to="properties.WindowView", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Угол обзора"
        verbose_name_plural = "Углы обзора"

    def __str__(self):
        return f"Угол {self.angle}"


class MiniPlanManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('type')


class MiniPlanPoint(models.Model):
    """ Модель точки на миниплане """

    ppoi = PpoiField(verbose_name="Точка на мини-плане", source="type.building.mini_plan")
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)
    type = models.ForeignKey(
        "properties.WindowViewType", models.CASCADE, verbose_name="Тип вида из окна"
    )
    objects = MiniPlanManger()

    class Meta:
        ordering = ("order",)
        verbose_name = "Точка на миниплане"
        verbose_name_plural = "Точки на миниплане"

    def __str__(self):
        return f"{self.order}, {self.type}"


class MiniPlanPointAngle(models.Model):
    """ Модель угла обзора на миниплане """

    angle = models.PositiveSmallIntegerField(
        verbose_name="Угол", validators=[MinValueValidator(1), MaxValueValidator(360)]
    )
    mini_plan = models.ForeignKey(
        verbose_name="Точка на мини-плане", to="properties.MiniPlanPoint", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Угол обзора на миниплане"
        verbose_name_plural = "Углы обзора на миниплане"

    def __str__(self):
        return f"Угол {self.angle}"

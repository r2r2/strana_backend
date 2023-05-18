from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from common.fields import ChoiceArrayField
from properties.constants import PropertyType
from .constants import FeedType


class FeedQuerySet(models.QuerySet):
    def filter_active(self):
        return self.filter(is_active=True).select_related("manager").prefetch_related("buildings")


class Feed(models.Model):
    objects = FeedQuerySet.as_manager()

    is_active = models.BooleanField("Активен", default=True)
    include_booked = models.BooleanField("Добавлять забронированные объекты", default=False)
    name = models.CharField("Название", max_length=128, db_index=True)
    slug = models.SlugField("Алиас", unique=True, db_index=True)
    description = models.TextField("Описание", blank=True)
    template_type = ChoiceArrayField(
        verbose_name="Типы шаблонов",
        base_field=models.CharField(choices=FeedType.choices, max_length=20),
        default=list,
    )
    property_type = models.CharField(
        verbose_name="Тип", max_length=20, choices=PropertyType.choices
    )
    manager = models.ForeignKey(
        "feeds.FeedManager",
        verbose_name="Менеджер фида",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    buildings = models.ManyToManyField("buildings.Building", verbose_name="Корпусы", blank=True)
    updated = models.DateTimeField("Изменен", auto_now=True)

    class Meta:
        verbose_name = "Фид"
        verbose_name_plural = "Фиды"

    def __str__(self):
        return f"{self.template_type} - тип недвижимости {self.get_property_type_display()}"


class FeedManager(models.Model):
    phone = PhoneNumberField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    first_name = models.CharField("Имя", max_length=64, blank=True)
    last_name = models.CharField("Фамилия", max_length=64, blank=True)
    organization = models.CharField("Организация", max_length=150, blank=True)

    class Meta:
        verbose_name = "Менеджер фида"
        verbose_name_plural = "Менеджеры фидов"

    def __str__(self):
        return f"{self.last_name + ' ' + self.first_name or self.phone}"

from django.db import models


class CityMenuThrough(models.Model):
    menu_city = models.OneToOneField(
        verbose_name="Меню",
        to="references.Menu",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="menu_city"
    )
    city = models.ForeignKey(
        verbose_name="Город",
        to="references.Cities",
        on_delete=models.CASCADE,
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "menus_menu_cities"
        unique_together = ('city', 'menu_city')
        verbose_name = "Групповой город-меню"
        verbose_name_plural = "Групповые города-меню"

    def __str__(self):
        return f"{self.menu_city} {self.city}"


class Cities(models.Model):
    """
    Города
    """
    name = models.CharField(verbose_name="Название", max_length=150)
    slug = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    timezone_offset: int = models.IntegerField(default=0, verbose_name="Разница временного пояса с UTC")
    menus_city = models.ManyToManyField(
        verbose_name="Меню",
        blank=True,
        to="references.Menu",
        through=CityMenuThrough,
        through_fields=("city", "menu_city"),
        related_name="menus_city"
    )
    users = models.ManyToManyField(
        blank=True,
        verbose_name="Пользователи",
        to="users.CabinetUser",
        through="users.CityUserThrough",
        through_fields=(
            "city",
            "user",
        ),
        related_name="city_users"
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "cities_city"
        verbose_name = "Город"
        verbose_name_plural = "13.1. [Общее] Города"

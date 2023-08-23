from django.db import models


class CityMenuThrough(models.Model):
    menu_city = models.ForeignKey(
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


class RoleMenuThrough(models.Model):
    menu_role = models.ForeignKey(
        verbose_name="Меню",
        to="references.Menu",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="menu_role"
    )
    role = models.ForeignKey(
        verbose_name="Роль",
        to="users.UserRole",
        on_delete=models.CASCADE,
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "menus_menu_roles"
        unique_together = ('menu_role', 'role')
        verbose_name = "Групповой роль-меню"
        verbose_name_plural = "Групповые роли-меню"

    def __str__(self):
        return f"{self.menu_role} {self.role}"


class Menu(models.Model):
    """
    Меню
    """
    name: str = models.CharField(verbose_name="Название пункта меню", null=False, max_length=50)
    link: str = models.CharField(verbose_name="Ссылка пункта меню", null=False, max_length=100)
    priority: int = models.IntegerField(verbose_name="Приоритет", null=False)
    cities = models.ManyToManyField(
        verbose_name="Города",
        blank=True,
        to='references.Cities',
        through=CityMenuThrough,
        through_fields=("menu_city", "city"),
        related_name="cities"
    )
    icon = models.FileField(verbose_name="Иконка", null=True, blank=True)
    roles = models.ManyToManyField(
        verbose_name="Роли",
        blank=True,
        to="users.UserRole",
        through=RoleMenuThrough,
        through_fields=("menu_role", "role"),
        related_name="roles"
    )
    hide_desktop: bool = models.BooleanField(verbose_name="Скрыть на десктопе", default=False)

    def __str__(self) -> str:
        return self.name

    def get_cities(self):
        return ",".join([str(p) for p in self.cities.all()])

    def get_roles(self):
        return ",".join([str(p) for p in self.roles.all()])

    class Meta:
        managed = False
        db_table = "menus_menu"
        verbose_name = "Меню"
        verbose_name_plural = "13.2. [Общее] Меню"
        ordering = ["priority"]


class Cities(models.Model):
    """
    Города
    """
    name = models.CharField(verbose_name="Название", max_length=150)
    slug = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    menus_city = models.ManyToManyField(
        verbose_name="Меню",
        blank=True,
        to="references.Menu",
        through=CityMenuThrough,
        through_fields=("city", "menu_city"),
        related_name="menus_city"
    )
    users = models.ManyToManyField(
        null=True, blank=True,
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

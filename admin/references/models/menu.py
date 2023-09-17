from django.db import models


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
        to="references.Cities",
        through="references.CityMenuThrough",
        through_fields=("menu_city", "city"),
        related_name="cities"
    )
    icon = models.FileField(verbose_name="Иконка", null=True, blank=True)
    roles = models.ManyToManyField(
        verbose_name="Роли",
        blank=True,
        to="users.UserRole",
        through="references.RoleMenuThrough",
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

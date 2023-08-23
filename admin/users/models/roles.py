from django.db import models

from references.models import RoleMenuThrough


class UserRole(models.Model):
    """
    Роль пользователя
    """

    name: str = models.CharField(
        max_length=200, blank=True, null=True, help_text="Роль пользователя", verbose_name="Роль"
    )
    menus_role = models.ManyToManyField(
        verbose_name="Меню",
        blank=True,
        to="references.Menu",
        through=RoleMenuThrough,
        through_fields=("role", "menu_role"),
        related_name="menus_role"
    )
    slug: str = models.CharField(max_length=50, verbose_name="slug", blank=False)

    def __str__(self) -> str:
        return self.name


    class Meta:
        managed = False
        db_table = "users_roles"
        verbose_name = "Роль"
        verbose_name_plural = " 2.5. [Справочник] Роли"

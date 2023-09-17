from django.db import models


class RoleMenuThrough(models.Model):
    menu_role = models.OneToOneField(
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

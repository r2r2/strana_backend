from django.db import models


class UserRole(models.Model):
    """
    Роль пользователя
    """

    name: str = models.CharField(
        max_length=200, blank=True, null=True, help_text="Роль пользователя", verbose_name="Роль"
    )

    def __str__(self) -> str:
        return self.name


    class Meta:
        managed = False
        db_table = "users_roles"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

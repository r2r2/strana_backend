from django.db import models


class UserLikeProperty(models.Model):
    """Избранные пользователей"""

    user = models.ForeignKey("users.User", models.CASCADE, verbose_name="Пользователь")
    property = models.ForeignKey("properties.Property", models.CASCADE, verbose_name="Помещение")
    date = models.DateTimeField("Дата добавления", auto_now=True)

    class Meta:
        unique_together = (("user", "property"),)
        ordering = ("-date",)

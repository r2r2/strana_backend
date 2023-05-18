from django.db import models
from projects.models import Project


class VkAccount(models.Model):
    """
    Аккаунт в инстраграме
    """

    id = models.CharField(verbose_name="ID", unique=True, primary_key=True, max_length=50)
    username = models.CharField(verbose_name="Username", max_length=50, blank=True)

    profile_image = models.ImageField(
        verbose_name="Изображение профиля", upload_to="vk/p_image", null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.username}"

    class Meta:
        verbose_name = "Аккаунт в вк"
        verbose_name_plural = "Аккаунты в вк"

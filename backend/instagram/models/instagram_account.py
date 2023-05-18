from django.db import models
from projects.models import Project


class InstagramAccount(models.Model):
    """
    Аккаунт в инстраграме
    """

    id = models.CharField(verbose_name="ID", unique=True, primary_key=True, max_length=50)
    username = models.CharField(verbose_name="Username", max_length=50, blank=True)
    first = models.PositiveSmallIntegerField(verbose_name="Количество", default=12)

    profile_image = models.ImageField(
        verbose_name="Изображение профиля", upload_to="instagram/p_image", null=True, blank=True
    )
    project = models.ForeignKey(verbose_name="Проект", to=Project, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.project.name} - {self.id}"

    class Meta:
        verbose_name = "Аккаунт в инстраграме"
        verbose_name_plural = "Аккаунты в инстаграме"

from django.db import models


class Camera(models.Model):
    """
    Камера
    """

    name = models.CharField(verbose_name="Имя", max_length=100)
    active = models.BooleanField(verbose_name="Активно", default=True)
    link = models.URLField(verbose_name="Ссылка", max_length=400)
    project = models.ForeignKey(
        verbose_name="Проект",
        to="projects.Project",
        on_delete=models.CASCADE,
        related_name="project_camera",
    )
    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Камера"
        verbose_name_plural = "Камеры"
        ordering = ("order",)

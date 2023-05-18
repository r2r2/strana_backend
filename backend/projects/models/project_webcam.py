from django.db import models


class ProjectWebcam(models.Model):
    """
    Веб-камеры проекта
    """

    name = models.CharField("Название", max_length=32)
    link = models.URLField("Ссылка")
    project = models.ForeignKey("projects.Project", verbose_name="Проект", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        ordering = ("order",)
        verbose_name = "Веб-камера проекта"
        verbose_name_plural = "Веб-камеры проекта"

    def __str__(self):
        return self.name

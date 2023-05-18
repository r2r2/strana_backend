from django.db import models


class ProjectBrochure(models.Model):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="brochures",
        verbose_name="проект"
    )
    file = models.FileField(
        upload_to="p/panel/brochures", verbose_name="файл брошюры"
    )

    class Meta:
        verbose_name = "брошюра проекта"
        verbose_name_plural = "брошюры проектов"

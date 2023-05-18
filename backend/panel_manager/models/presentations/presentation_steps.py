from django.db import models


class PresentationSteps(models.Model):
    presentationstage = models.ForeignKey(
        "panel_manager.PresentationStage", models.CASCADE, verbose_name="Блок презентации"
    )
    aboutprojectgallerycategory = models.ForeignKey(
        "panel_manager.AboutProjectGalleryCategory",
        models.CASCADE,
        verbose_name="Категория презентации",
    )

    order = models.PositiveIntegerField("Очередность", default=0)

    class Meta:
        verbose_name = "Шаг презентации"
        verbose_name_plural = "Шаги презентации"
        ordering = ("order",)

    def __str__(self):
        return f"{self.presentationstage} = {self.aboutprojectgallerycategory}"

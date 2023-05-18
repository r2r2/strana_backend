from django.db import models


class PresentationStageType(models.IntegerChoices):
    """Типы Блока"""

    INVEST = 0, "Для инвестиций"
    LIVE = 1, "Для собственного проживания"
    BEAUTIFI = 3, "Благоустройство"
    OTHER = 4, "Другое"
    TRANSPORT = 5, "Транспортная доступность"
    MORTGAGE = 6, "Ипотека"
    PAY = 7, "100% оплата"


class PresentationStage(models.Model):
    """Блок построения презентации"""

    # project = models.ForeignKey("projects.Project", models.CASCADE, verbose_name="Проект")

    stage_number = models.PositiveIntegerField("Номер в стадии", default=0)
    hard_type = models.IntegerField(
        "Тип", choices=PresentationStageType.choices, blank=True, null=True
    )

    name = models.CharField("Наименование", max_length=200)
    image = models.ImageField("Изображение", upload_to="pm/ps/i", blank=True)
    description = models.TextField("Описание", blank=True)

    about_project_slides = models.ManyToManyField(
        "panel_manager.AboutProjectGalleryCategory",
        verbose_name="Категория слайдов",
        blank=True,
        through="panel_manager.PresentationSteps",
        through_fields=("presentationstage", "aboutprojectgallerycategory"),
        related_name="aboutprojectgallerycategory_rm",
    )

    class Meta:
        verbose_name = "Блок построения презентации"
        verbose_name_plural = "Блоки построения презентации"

    def __str__(self):
        return self.name

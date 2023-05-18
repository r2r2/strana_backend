from django.db import models


class Document(models.Model):
    """
    Документ
    """

    date = models.DateTimeField(verbose_name="Дата размещения")
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    file = models.FileField(verbose_name="Файл", upload_to="document/file")
    is_investors = models.BooleanField(verbose_name="Вывести на страницу инвесторам", default=False)
    category = models.ForeignKey(
        verbose_name="Категория", to="company.DocumentCategory", on_delete=models.CASCADE
    )
    building = models.ForeignKey(
        verbose_name="Корпус",
        to="buildings.Building",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        verbose_name="Проект",
        to="projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Отображается во всех городах, если не указан проект.",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ("-date",)

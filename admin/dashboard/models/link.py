from django.db import models


class Link(models.Model):
    """
    Ссылка
    """
    link: str = models.TextField(verbose_name="Ссылка", null=True, blank=True)
    element: models.ForeignKey = models.ForeignKey(
        to="dashboard.Element",
        verbose_name="Элемент",
        related_name="links",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    city: models.ManyToManyField = models.ManyToManyField(
        to="references.Cities",
        verbose_name="Город",
        related_name="links",
        help_text="Город",
        through="LinkCityThrough",
        through_fields=("link", "city"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
        help_text="Время создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
        help_text="Время последнего обновления",
    )

    def __str__(self) -> str:
        return self.link

    class Meta:
        managed = False
        db_table = "dashboard_link"
        verbose_name = "Ссылка"
        verbose_name_plural = "12.3. Ссылки"


class LinkCityThrough(models.Model):
    """
    Связь ссылки и города
    """
    link: models.ForeignKey = models.ForeignKey(
        to="dashboard.Link",
        verbose_name="Ссылка",
        related_name="link_through",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    city: models.ForeignKey = models.ForeignKey(
        to="references.Cities",
        verbose_name="Город",
        related_name="link_through",
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = "dashboard_link_city_through"
        verbose_name = "Связь ссылки и города"
        verbose_name_plural = "Связи ссылок и городов"

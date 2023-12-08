from django.db import models


class NewsTag(models.Model):
    """
    Новости.
    """

    label: str = models.CharField(
        verbose_name="Название тега",
        max_length=100,
    )
    slug: str = models.CharField(
        verbose_name="Слаг тега",
        max_length=100,
        unique=True,
    )
    is_active = models.BooleanField(verbose_name="Тег активен", default=True)
    priority = models.IntegerField(verbose_name="Приоритет", default=0)

    def __str__(self) -> str:
        return self.label

    class Meta:
        managed = False
        db_table = "news_news_tag"
        verbose_name = "Теги новостей"
        verbose_name_plural = "20.2. Теги"
        ordering = ["priority"]

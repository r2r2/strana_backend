from django.db import models


class SearchQuery(models.Model):
    """ Модель поискового запроса пользователя """

    body = models.TextField(verbose_name="Тело запроса")
    url = models.URLField(
        verbose_name="Страница запроса", help_text="с которой был отправлен запрос"
    )
    created = models.DateTimeField(verbose_name="Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Поисковый запрос"
        verbose_name_plural = "Поисковые запросы"

    def __str__(self) -> str:
        return f"Запрос №{self.id}"

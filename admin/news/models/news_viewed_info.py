from django.db import models


class NewsViewedInfo(models.Model):
    """
    Просмотренные новости.
    """

    news: models.ForeignKey = models.ForeignKey(
        to="news.News",
        on_delete=models.CASCADE,
        related_name='news_viewed_info',
        verbose_name="Новость",
    )
    user: models.ForeignKey = models.ForeignKey(
        to='users.CabinetUser',
        on_delete=models.CASCADE,
        related_name='news_viewed_info',
        verbose_name="Пользователь",
    )
    viewing_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время просмотра",
    )
    is_voice_left: bool = models.BooleanField(verbose_name="Пользователь проголосовал под новостью", default=False)
    is_useful = models.BooleanField(
        verbose_name="Новость была полезной",
        default=False,
        help_text="Вкл - если новость полезна, Выкл - если нет (при условии того, что пользователь проголосовал)",
    )

    def __str__(self) -> str:
        return f"Инфо о просмотре, id - {self.id}"

    class Meta:
        managed = False
        db_table = "news_news_viewed_info"
        verbose_name = "Отслеживание просмотров новостей"
        verbose_name_plural = "20.3. Отслеживание просмотров новостей"

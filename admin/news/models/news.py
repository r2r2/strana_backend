from django.db import models
from ckeditor.fields import RichTextField


class News(models.Model):
    """
    Новости.
    """

    title: str = models.CharField(verbose_name="Заголовок новости", max_length=150)
    slug: str = models.CharField(
        verbose_name="Слаг новости",
        max_length=100,
        unique=True,
    )
    short_description = models.TextField(verbose_name="Краткое описание новости", blank=True)
    description = RichTextField(verbose_name="Описание новости")
    is_active = models.BooleanField(verbose_name="Новость активна", default=True)
    image_preview = models.FileField(
        verbose_name="Изображение (превью)",
        upload_to='n/i/p',
        null=True,
        blank=True,
    )
    image = models.FileField(
        verbose_name="Изображение",
        upload_to='n/i/i',
        null=True,
        blank=True,
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации новости",
    )
    end_date = models.DateTimeField(
        verbose_name="Дата окончания новости",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        help_text='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
        help_text='Время последнего обновления'
    )

    tags = models.ManyToManyField(
        verbose_name="Теги",
        to="news.NewsTag",
        through="news.NewsNewsTagThrough",
        through_fields=("news", "news_tag"),
        related_name="news",
        blank=True,
    )
    roles = models.ManyToManyField(
        verbose_name="Роли",
        to="users.UserRole",
        through="news.NewsUserRoleThrough",
        through_fields=("news", "role"),
        related_name="news",
    )
    projects = models.ManyToManyField(
        verbose_name="Проекты",
        to="properties.Project",
        through="news.NewsProjectThrough",
        through_fields=("news", "project"),
        related_name="news"
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        managed = False
        db_table = "news_news"
        verbose_name = "Новости"
        verbose_name_plural = "20.1. Новости"
        ordering = ["pub_date"]


class NewsNewsTagThrough(models.Model):
    """
    Выбранные теги для новостей.
    """

    news: models.ForeignKey = models.ForeignKey(
        to=News,
        on_delete=models.CASCADE,
        related_name='news_tag_through',
    )
    news_tag: models.ForeignKey = models.ForeignKey(
        to='news.NewsTag',
        on_delete=models.CASCADE,
        related_name='news_through',
    )

    class Meta:
        managed = False
        db_table = 'news_news_tag_through'


class NewsUserRoleThrough(models.Model):
    """
    Выбранные роли пользователей для новостей.
    """

    news: models.ForeignKey = models.ForeignKey(
        to=News,
        on_delete=models.CASCADE,
        related_name='user_role_through',
    )
    role: models.ForeignKey = models.ForeignKey(
        to='users.UserRole',
        on_delete=models.CASCADE,
        related_name='news_through',
    )

    class Meta:
        managed = False
        db_table = 'news_news_user_role_through'


class NewsProjectThrough(models.Model):
    """
    Выбранные проекты для новостей.
    """

    news: models.ForeignKey = models.ForeignKey(
        to=News,
        on_delete=models.CASCADE,
        related_name='project_through',
    )
    project: models.ForeignKey = models.ForeignKey(
        to='properties.Project',
        on_delete=models.CASCADE,
        related_name='news_through',
    )

    class Meta:
        managed = False
        db_table = 'news_news_project_through'

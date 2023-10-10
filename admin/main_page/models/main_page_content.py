from ckeditor.fields import RichTextField
from django.db import models


class MainPageContent(models.Model):
    """
    Контент и заголовки главной страницы
    """
    title = models.TextField(
        verbose_name="Заголовок блока",
        blank=True,
        help_text="H1 заголовок страницы / слайд-панели",
    )
    text = RichTextField(
        verbose_name="Текст блока главной страницы",
        null=True,
        blank=True,
    )
    slug: str = models.CharField(
        max_length=50,
        verbose_name='Слаг текстового блока',
        help_text="Определяет место на странице, "
                  "куда подставляется текст (максимум 50 символов)",
        unique=True,
    )
    comment = models.TextField(
        verbose_name="Описание назначения текстового блока",
        blank=True,
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
    )

    created_at = models.DateTimeField(
        verbose_name="Когда создано",
        help_text="Когда создано",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Когда обновлено",
        help_text="Когда обновлено",
        auto_now=True,
    )

    def __str__(self) -> str:
        return self.slug

    class Meta:
        db_table = 'main_page_content'
        verbose_name = "Контент и заголовки"
        verbose_name_plural = "16.1. Контент и заголовки"

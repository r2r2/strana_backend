from ckeditor.fields import RichTextField
from django.db import models


class MainPageContent(models.Model):
    """
    Контент и заголовки главной страницы
    """

    text: str = RichTextField(verbose_name="Текст главной страницы")
    slug: str = models.CharField(
        max_length=50,
        verbose_name='Slug',
        help_text="Определяет место на странице, куда подставляется текст",
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Внутренний комментарий',
        help_text='Внутренний комментарий',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.slug

    class Meta:
        managed = False
        db_table = 'main_page_content'
        verbose_name = "Контент и заголовки"
        verbose_name_plural = "16.1. Контент и заголовки"

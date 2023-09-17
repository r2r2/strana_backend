from ckeditor.fields import RichTextField
from django.db import models


class MainPageOffer(models.Model):
    """
    Блок: Что мы предлагаем
    """
    title: str = models.CharField(verbose_name="Заголовок", max_length=255, null=True, blank=True)
    description: str = RichTextField(verbose_name="Описание", null=True, blank=True)
    image: str = models.ImageField(verbose_name="Изображение", max_length=500, null=True, blank=True)
    priority: int = models.IntegerField(
        verbose_name="Приоритет",
        help_text="Определяет порядок вывода объектов",
        null=True,
        blank=True,
    )
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Неактивные объекты не выводятся"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'main_page_offer'
        verbose_name = "Что мы предлагаем"
        verbose_name_plural = "16.2. Блок: Что мы предлагаем"

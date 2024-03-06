from django.db import models


class PrivilegeInfo(models.Model):
    """
    Основная информация
    """

    title: str = models.CharField(max_length=250, verbose_name="Название")
    slug: str = models.CharField(max_length=250, verbose_name="Слаг", primary_key=True)
    description: str = models.TextField(verbose_name="Описание", blank=True)
    image: str = models.ImageField(verbose_name="Изображение", max_length=500, null=True, blank=True)

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

    def __str__(self) -> str:
        return self.slug

    class Meta:
        managed = False
        db_table = 'privilege_info'
        verbose_name = "Общая информация"
        verbose_name_plural = "22.7 Общая информация"


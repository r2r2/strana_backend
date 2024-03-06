from django.db import models


class PrivilegeBenefit(models.Model):
    """
    Преимущества
    """

    title: str = models.CharField(max_length=250, verbose_name="Название")
    slug: str = models.CharField(max_length=250, verbose_name="Слаг", primary_key=True)
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Выводить на фронт или нет"
    )
    priority: int = models.IntegerField(
        verbose_name="Приоритет", default=0, help_text="Порядок вывода на фронт"
    )
    image: str = models.FileField(
        verbose_name="Изображение",
        max_length=500,
        upload_to="d/d/p",
        null=True,
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

    def __str__(self) -> str:
        return self.slug

    class Meta:
        managed = False
        db_table = 'privilege_benefit'
        verbose_name = "Преимущества"
        verbose_name_plural = "22.8 Преимущества"


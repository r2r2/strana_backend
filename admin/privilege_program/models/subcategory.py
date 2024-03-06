from django.db import models


class PrivilegeSubCategory(models.Model):
    """
    Подкатегория программ привилегий
    """

    title: str = models.CharField(max_length=250, verbose_name="Название")
    slug: str = models.CharField(max_length=250, verbose_name="Слаг", primary_key=True)
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Выводить на фронт или нет"
    )
    category: models.ForeignKey = models.ForeignKey(
        to="privilege_program.PrivilegeCategory",
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Категория",
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
        db_table = 'privilege_subcategory'
        verbose_name = "Подкатегория программ"
        verbose_name_plural = "22.3 Подкатегории программ"


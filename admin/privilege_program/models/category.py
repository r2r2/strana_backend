from django.db import models


class PrivilegeCategory(models.Model):
    """
    Категория программ привилегий
    """

    class DisplayType(models.TextChoices):
        ONE_TO_THREE: tuple[str] = "1to3", "1 к 3"
        TWO_TO_THREE: tuple[str] = "2to3", "2 к 3"

    title: str = models.CharField(max_length=250, verbose_name="Название")
    slug: str = models.CharField(max_length=250, verbose_name="Слаг", primary_key=True)
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Выводить на фронт или нет"
    )
    dashboard_priority: int = models.IntegerField(
        verbose_name="Приоритет на дашборде", default=0, help_text="Порядок вывода на фронт"
    )
    filter_priority: int = models.IntegerField(
        verbose_name="Приоритет в фильтре", default=0, help_text="Порядок вывода на фронт"
    )
    cities: models.ManyToManyField = models.ManyToManyField(
        to="references.Cities",
        verbose_name='Города',
        related_name='privilege_categories',
        help_text='Города',
        blank=True,
        null=True,
        through='PrivilegeCategoryM2MCity',
        through_fields=('privilege_category', 'city'),
    )

    image: str = models.ImageField(verbose_name="Изображение", max_length=500, null=True, blank=True)
    display_type: str = models.CharField(
        verbose_name="Отображение карточки", max_length=250,
        choices=DisplayType.choices,
        default=DisplayType.ONE_TO_THREE,
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
        db_table = 'privilege_category'
        verbose_name = "Категория программ"
        verbose_name_plural = "22.2 Категории программ"


class PrivilegeCategoryM2MCity(models.Model):
    """
    Связь Категорий Программы привилегий и городов.
    """
    privilege_category: models.ForeignKey = models.ForeignKey(
        to='privilege_program.PrivilegeCategory',
        verbose_name='Категория программ',
        related_name='privilege_category_m2m_city',
        on_delete=models.CASCADE,
        to_field="slug",
        primary_key=True,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        verbose_name='Город',
        related_name='privilege_category_m2m_city',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'privilege_category_m2m_city'

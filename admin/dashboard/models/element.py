from datetime import datetime

from django.db import models


class Element(models.Model):
    """
    Элемент
    """
    type: str = models.CharField(verbose_name="Тип", max_length=255, null=True, blank=True)
    width: int = models.IntegerField(verbose_name="Ширина", null=True, blank=True)
    title: str = models.CharField(verbose_name="Заголовок", max_length=255, null=True, blank=True)
    description: str = models.TextField(verbose_name="Описание", null=True, blank=True)
    image: str = models.ImageField(verbose_name="Изображение", max_length=500, null=True, blank=True)
    expires: datetime = models.DateTimeField(verbose_name="Истекает", null=True, blank=True)
    has_completed_booking: bool = models.BooleanField(verbose_name="Бронирование завершено", default=False)
    slug: str = models.CharField(max_length=15, null=True)

    block: models.ForeignKey = models.ForeignKey(
        to='dashboard.Block',
        verbose_name='Блок',
        related_name='elements',
        on_delete=models.CASCADE,
    )
    city: models.ManyToManyField = models.ManyToManyField(
        to='references.Cities',
        verbose_name='Город',
        related_name='elements',
        help_text='Город',
        through='ElementCityThrough',
        through_fields=('element', 'city'),
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
        return self.type

    class Meta:
        managed = False
        db_table = 'dashboard_element'
        verbose_name = 'Элемент'
        verbose_name_plural = '12.4. Элементы'


class ElementCityThrough(models.Model):
    """
    Связь элемента и города
    """
    element: models.ForeignKey = models.ForeignKey(
        to='dashboard.Element',
        verbose_name='Элемент',
        related_name='element_city_through',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        verbose_name='Город',
        related_name='element_city_through',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'dashboard_element_city_through'
        verbose_name = 'Связь элемента и города'
        verbose_name_plural = 'Связи элементов и городов'
from django.db import models


class Block(models.Model):
    """
    Блок
    """

    class BlockType(models.TextChoices):
        SEPARATE_CARD_SLIDER: tuple[str] = "separate_card_slider", "слайдер на 3 карточки в ряд"
        CARD_WITH_TIMEOUT_LINE_SLIDER: tuple[str] = "card_with_timeout_line_slider", "Слайдер для предложений"
        BACKGROUND_IMAGE_SLIDER: tuple[str] = "background_image_slider", "Как происходит покупка"
        STOCK_SLIDER: tuple[str] = "stock_slider", "Слайдер акции"
        PARKING: tuple[str] = "parking", "Паркинг"
        CARD: tuple[str] = "card", "Одиночная карточка"

    type: str = models.CharField(verbose_name="Тип", max_length=255, null=True, blank=True, choices=BlockType.choices)
    width: int = models.IntegerField(verbose_name="Ширина", null=True, blank=True)
    title: str = models.CharField(verbose_name="Заголовок", max_length=255, null=True, blank=True)
    description: str = models.TextField(verbose_name="Описание", null=True, blank=True)
    image: str = models.ImageField(verbose_name="Изображение", max_length=500, null=True, blank=True)
    priority: int = models.IntegerField(verbose_name="Приоритет", null=True, blank=True)
    city: models.ManyToManyField = models.ManyToManyField(
        to="references.Cities",
        verbose_name='Город',
        related_name='blocks',
        help_text='Город',
        through='BlockCityThrough',
        through_fields=('block', 'city'),
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
        return self.title

    class Meta:
        managed = False
        db_table = 'dashboard_block'
        verbose_name = 'Блок'
        verbose_name_plural = '12.1. Блоки'


class BlockCityThrough(models.Model):
    """
    Связь блока и города
    """
    block: models.ForeignKey = models.ForeignKey(
        to='dashboard.Block',
        verbose_name='Блок',
        related_name='block_city_through',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        verbose_name='Город',
        related_name='block_city_through',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'dashboard_block_city_through'
        verbose_name = 'Связь блока и города'
        verbose_name_plural = 'Связи блоков и городов'


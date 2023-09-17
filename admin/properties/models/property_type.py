from django.db import models


class PropertyType(models.Model):
    """
    Модель типа объектов недвижимости.
    """

    sort = models.IntegerField(
        verbose_name='Приоритет',
        default=0,
        help_text='Определяет порядок вывода объектов недвижимости в интерфейсах',
    )
    slug = models.CharField(verbose_name='Слаг', max_length=20, unique=True)
    label = models.CharField(verbose_name='Название типа', max_length=40)
    is_active = models.BooleanField(
        verbose_name='Активность',
        default=True,
        help_text='Неактивные объекты недвижимости не выводятся в интерфейсах сайта',
    )
    pipelines = models.ManyToManyField(
        verbose_name="Воронки сделок",
        to="booking.AmocrmPipeline",
        through="PropertyTypePipelineThrough",
        through_fields=("property_type", "pipeline"),
        related_name="property_type_pipelines",
        blank=True,
    )

    def __str__(self):
        return self.label

    class Meta:
        managed = False
        db_table = "properties_property_type"
        ordering = ("sort",)
        verbose_name = "Тип объектов недвижимости"
        verbose_name_plural = "3.6. [Справочник] Типы объектов недвижимости"


class PropertyTypePipelineThrough(models.Model):
    """
    Промежуточная таблица для связи типа объекта недвижимости и воронки.
    """
    property_type = models.OneToOneField(
        to="properties.PropertyType",
        on_delete=models.CASCADE,
        related_name="pipeline",
        primary_key=True,
    )
    pipeline = models.ForeignKey(
        to="booking.AmocrmPipeline",
        verbose_name="Воронка",
        on_delete=models.CASCADE,
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "properties_property_type_pipelines"
        verbose_name = "Тип объекта - Воронка"
        verbose_name_plural = "Тип объекта - Воронки"
        unique_together = ('property_type', 'pipeline')

from django.db import models
from ckeditor.fields import RichTextField


class AdditionalService(models.Model):
    """
    Доп услуга
    """

    title: str = models.CharField(max_length=150, null=True, verbose_name="Название")
    priority: int = models.IntegerField(default=0, verbose_name="Приоритет")
    image_preview = models.ImageField(
        max_length=500, null=True, upload_to="p/br/i", verbose_name="Превью изображения"
    )
    image_detailed = models.ImageField(
        max_length=500,
        null=True,
        upload_to="p/br/i",
        verbose_name="Детальное изображение",
    )
    announcement: str = models.TextField(verbose_name="Анонс")
    description: str = RichTextField(
        verbose_name="Подробная информация",
        null=True,
        help_text="Текст описания для услуги",
    )
    condition: models.ForeignKey = models.ForeignKey(
        to="additional_services.AdditionalServiceCondition",
        related_name="service_condition",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Как получить услуги",
    )
    category: models.ForeignKey = models.ForeignKey(
        to="additional_services.AdditionalServiceCategory",
        related_name="service_category",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория услуги",
    )
    active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Скрыть/Показать услугу"
    )
    group_status = models.ForeignKey(
        to="booking.AmocrmGroupStatus",
        related_name="service_group_status",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Статус в Амо",
    )
    hint: str = models.TextField(verbose_name="Текст подсказки")
    kind: models.ForeignKey = models.ForeignKey(
        to="additional_services.AdditionalServiceType",
        related_name="service_type",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Тип сервиса",
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "additional_services_service"
        verbose_name = "услуга"
        verbose_name_plural = "17.2. [Справочник] Услуги"

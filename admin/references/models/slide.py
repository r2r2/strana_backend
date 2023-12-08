from django.db import models

class Slide(models.Model):
    """
    Слайд
    """

    is_active: bool = models.BooleanField(verbose_name="Активность", default=True)

    priority: int = models.IntegerField(default=0, verbose_name='Приоритет')

    title = models.CharField(
        verbose_name="Заголовок слайда", max_length=300, null=True
    )

    subtitle = models.CharField(
        verbose_name="Подзаголовок слайда", max_length=300, null=True
    )

    desktop_media = models.FileField(
        verbose_name="Картинка/видео для десктопа", upload_to="r/m/s", max_length=300, null=True,
    )

    tablet_media = models.FileField(
        verbose_name="Картинка/видео для планшета", upload_to="r/m/s", max_length=300, null=True,
    )

    mobile_media = models.FileField(
        verbose_name="Картинка/видео для мобильной версии", upload_to="r/m/s", max_length=300, null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "slider_auth"
        verbose_name = "Слайд"
        verbose_name_plural = "13.5. [ЛК Клиента] Слайдер на странице авторизации"
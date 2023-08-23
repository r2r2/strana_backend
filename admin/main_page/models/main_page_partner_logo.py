from django.db import models


class MainPagePartnerLogo(models.Model):
    """
    Блок: Логотипы партнеров
    """
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
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'main_page_partner_logo'
        verbose_name = "Логотипы партнеров"
        verbose_name_plural = "16.3. Блок: Логотипы партнеров"

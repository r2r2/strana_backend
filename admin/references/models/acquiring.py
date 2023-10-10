from django.db import models


class Acquiring(models.Model):
    """
    Эквайринг
    """
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        related_name='acquiring',
        on_delete=models.CASCADE,
        verbose_name='Город',
        help_text="Город, к которому подключен эквайринг",
    )
    is_active: bool = models.BooleanField(verbose_name="Активный", default=False)
    username: str = models.CharField(verbose_name="Имя пользователя", max_length=100, null=False)
    password: str = models.CharField(verbose_name="Пароль", max_length=200, null=False)

    def __str__(self) -> str:
        return self.city.name

    class Meta:
        managed = False
        db_table = "booking_acquiring"
        unique_together = ('city', 'is_active')
        verbose_name = "Эквайринг"
        verbose_name_plural = "13.4. [Общее] Эквайринг"

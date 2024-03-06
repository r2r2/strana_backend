from django.db import models


class UserInterestType(models.TextChoices):
    """
    Тип пользователя, добавившего запись в избранное.
    """

    MANAGER = "manager", "Менеджер"
    MINE = "mine", "Клиент"


class UsersInterests(models.Model):
    """
    Избранное пользователей.
    """

    user = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        verbose_name="Клиент",
    )
    property = models.ForeignKey(
        "properties.Property",
        models.CASCADE,
        verbose_name="Объект недвижимости",
    )
    interest_final_price = models.BigIntegerField(verbose_name="Конечная цена", null=True, blank=True)
    interest_status = models.SmallIntegerField(verbose_name="Статус", null=True, blank=True)
    interest_special_offers = models.TextField(verbose_name="Акции", null=True, blank=True)
    slug = models.CharField(
        choices=UserInterestType.choices,
        default=UserInterestType.MINE,
        max_length=20,
        verbose_name="Кто добавил",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        'users.CabinetUser',
        models.CASCADE,
        verbose_name='Кем создано',
        related_name='created_favorites',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", auto_now_add=True)

    def __str__(self):
         return f"Избранное пользователя: {self.user.full_name()} - {self.property}"

    class Meta:
        managed = False
        db_table = "users_interests"
        verbose_name = "Избранное пользователей"
        verbose_name_plural = "2.13. [Справочник] Избранное пользователей"

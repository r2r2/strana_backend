from django.db import models


class CityUserThrough(models.Model):
    city = models.ForeignKey(
        verbose_name="Город",
        to="references.Cities",
        on_delete=models.CASCADE,
        db_column="city_id",
        related_name="cities_through",
        primary_key=True,
    )
    user = models.ForeignKey(
        to="users.CabinetUser",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        db_column="user_id",
        unique=False,
        related_name="users_through"
    )

    class Meta:
        managed = False
        db_table = "users_cities"

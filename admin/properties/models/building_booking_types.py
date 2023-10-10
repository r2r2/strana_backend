from django.db import models


class BuildingBookingTypeThrough(models.Model):
    building = models.OneToOneField(
        verbose_name="Корпус",
        to="properties.Building",
        db_column="buildings_building_id",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="building",
    )
    booking_type = models.ForeignKey(
        verbose_name="Тип бронирования",
        to="properties.BuildingBookingType",
        db_column="buildingbookingtype_id",
        on_delete=models.CASCADE,
        unique=False,
        related_name="booking_type",
    )

    class Meta:
        managed = False
        db_table = "building_building_booking_type_m2m"
        unique_together = ("building", "booking_type")


class BuildingBookingType(models.Model):
    """
    Тип бронирования у корпусов.
    """

    period: int = models.IntegerField(verbose_name="Длительность бронирования")
    price: int = models.IntegerField(verbose_name="Стоимость бронирования")
    amocrm_id = models.BigIntegerField(verbose_name="Идентификатор АМОЦРМ", null=True)
    priority = models.IntegerField(
        verbose_name="Приоритет вывода (чем меньше чем, тем раньше)", null=True
    )

    def __str__(self) -> str:
        return f"Длительность: {self.period}, стоимость: {self.price}"

    class Meta:
        managed = False
        db_table = "buildings_building_booking_type"
        verbose_name = "тип бронирования"
        verbose_name_plural = "Типы бронирования"

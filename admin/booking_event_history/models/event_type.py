from django.db import models


class EventType(models.Model):
    """
    23.3 Тип событий
    """
    event_type_name: str = models.CharField(
        verbose_name="Название",
        max_length=150,
        unique=True
    )
    slug: str = models.CharField(
        verbose_name="Слаг события",
        max_length=100,
    )

    def __str__(self) -> str:
        return f"{self.event_type_name}"

    class Meta:
        verbose_name = "Тип события"
        verbose_name_plural = "23.3 Тип событий"
        db_table = "booking_event_type"

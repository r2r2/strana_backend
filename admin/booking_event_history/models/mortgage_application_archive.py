from datetime import datetime

from django.db import models


class MortgageApplicationArchive(models.Model):
    external_code: int = models.IntegerField(verbose_name="ID заявки в ИК")
    booking_id: int = models.IntegerField(verbose_name="ID брони")
    mortgage_application_status_until: str = models.CharField(
        verbose_name="Статус заявки на ипотеку До",
        max_length=150
    )
    mortgage_application_status_after: str = models.CharField(
        verbose_name="Статус заявки на ипотеку После",
        max_length=150
    )
    status_change_date: datetime = models.DateTimeField(
        verbose_name="Время изменения статуса",
        auto_now_add=True
    )

    def __str__(self) -> str:
        return f"Архив {self.pk}. Бронь: {self.booking_id}"

    class Meta:
        verbose_name = "Архив заявок на ипотеку"
        verbose_name_plural = "23.4 Архив заявок на ипотеку"
        db_table = "mortgage_application_archive"

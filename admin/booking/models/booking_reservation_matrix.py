from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingReservationMatrix(models.Model):
    """
    Матрица сроков резервирования
    """
    class BookingCreatedSources(models.TextChoices):
        """
        Источники создания бронирования
        """
        AMOCRM = "amocrm", _("Импортирован из AMOCRM")
        LK = "lk_booking", _("Бронирование через личный кабинет")
        LK_ASSIGN = "lk_booking_assign", _("Закреплен в ЛК Брокера")
        FAST_BOOKING = "fast_booking", _("Быстрое бронирование")

    project = models.ManyToManyField(
        to="properties.Project",
        related_name="booking_reservation_matrix",
        verbose_name="Проекты",
        null=True,
        blank=True,
        through="BookingReservationMatrixProjects",
    )
    created_source = models.CharField(
        choices=BookingCreatedSources.choices,
        default=BookingCreatedSources.AMOCRM,
        max_length=100,
        verbose_name="Источник создания онлайн-бронирования",
    )
    reservation_time = models.FloatField(verbose_name="Время резервирования квартир (ч)", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "booking_reservation_matrix"
        verbose_name = "Матрица сроков резервирования"
        verbose_name_plural = "1.7. [Справочник] Матрица сроков резервирования"


class BookingReservationMatrixProjects(models.Model):
    """
    Матрица сроков резервирования
    """
    reservation_matrix = models.ForeignKey(
        "BookingReservationMatrix",
        on_delete=models.CASCADE,
        verbose_name="Матрица сроков резервирования",
        related_name="booking_reservation_matrix_projects",
    )
    project = models.ForeignKey(
        "properties.Project",
        on_delete=models.CASCADE,
        verbose_name="Проект",
        related_name="booking_reservation_matrix_projects",
    )

    class Meta:
        managed = False
        db_table = "booking_reservation_matrix_projects"

from django.db import models

from .base_agreement import BaseAgreement


class AgencyAct(BaseAgreement):
    """
    Акт агентства
    """

    booking = models.ForeignKey(
        "booking.Booking",
        models.CASCADE,
        verbose_name="Бронь",
        help_text="Бронь"
    )
    agency = models.ForeignKey(
        "users.Agency",
        models.CASCADE,
        related_name='acts',
        verbose_name='Агентство',
        help_text='Агентство'
    )
    project = models.ForeignKey(
        "properties.Project",
        models.SET_NULL,
        verbose_name="Проект",
        help_text="Проект",
        null=True,
    )
    created_by = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="created_acts",
        verbose_name="Кем создано",
        help_text="Кем создано"
    )
    updated_by = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="updated_acts",
        verbose_name="Кем изменено",
        help_text="Кем изменено"
    )

    class Meta:
        db_table = "agencies_act"
        verbose_name = "Акт агентства"
        verbose_name_plural = " 7.1. Акты"

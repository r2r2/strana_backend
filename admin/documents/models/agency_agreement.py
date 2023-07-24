from django.db import models

from .base_agreement import BaseAgreement


class AgencyAgreement(BaseAgreement):
    """
    Договор агентства
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
        related_name='agreements',
        verbose_name='Агентство',
        help_text='Агентство'
    )
    project = models.ForeignKey(
        "properties.Project",
        models.CASCADE,
        verbose_name="Проект",
        help_text="Проект"
    )
    agreement_type = models.ForeignKey(
        "documents.AgreementType",
        models.CASCADE,
        verbose_name="Тип документа"
    )
    created_by = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="created_agreements",
        verbose_name="Кем создано",
        help_text="Кем создано"
    )
    updated_by = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="updated_agreements",
        verbose_name="Кем изменено",
        help_text="Кем изменено"
    )

    class Meta:
        db_table = "agencies_agreement"
        verbose_name = "Договор агентства"
        verbose_name_plural = " 7.2. Договора"

from django.db import models


class MortgageDeveloperTicket(models.Model):
    """
    Заявка через застройщика.
    """
    offers: models.ManyToManyField = models.ManyToManyField(
        to="mortgage.MortgageOffer",
        through="MortgageDeveloperTicketOfferThrough",
        related_name="mortgage_dev_tickets",
        verbose_name="Ипотечные предложения",
        blank=True,
        through_fields=("mortgage_dev_ticket", "mortgage_offer"),
    )
    status: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageApplicationStatus",
        on_delete=models.CASCADE,
        related_name="mortgage_dev_ticket",
        verbose_name="Статус заявки",
        null=True,
        blank=True,
    )
    calculator_condition: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageCalculatorCondition",
        on_delete=models.CASCADE,
        related_name="mortgage_dev_ticket",
        verbose_name="Условие в калькуляторе",
        null=True,
        blank=True,
    )
    form_data: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageForm",
        on_delete=models.CASCADE,
        related_name="mortgage_dev_ticket",
        verbose_name="Данные с формы",
        null=True,
        blank=True,
    )
    booking: models.ForeignKey = models.ForeignKey(
        to="booking.Booking",
        on_delete=models.CASCADE,
        related_name="mortgage_dev_tickets",
        verbose_name="Бронь",
    )

    def __str__(self) -> str:
        return f"Заявка на ипотеку через застройщика {self.id}"

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_developer_ticket'
        verbose_name = "Заявка на ипотеку"
        verbose_name_plural = "21.2. Заявка на ипотеку через застройщика"


class MortgageDeveloperTicketOfferThrough(models.Model):
    """
    Выбранные предложения.
    """
    mortgage_dev_ticket: models.ForeignKey = models.ForeignKey(
        to="MortgageDeveloperTicket",
        on_delete=models.CASCADE,
        related_name="mortgage_dev_ticket_offer_through",
    )
    mortgage_offer: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageOffer",
        on_delete=models.CASCADE,
        related_name="mortgage_offer_dev_ticket_through",
    )

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_dev_ticket_offer_through'

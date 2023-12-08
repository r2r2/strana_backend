from typing import Optional
from django.db import models

class MortgageTicket(models.Model):
    """
    Ticket под ипотечный калькулятор.
    """
    id =  models.BigIntegerField(verbose_name="ID", primary_key=True)

    # offer_statuses: models.ManyToManyField(
    #     verbose_name="Статусы сделки",
    #     to="properties.MortgageType",
    #     through="mortgage.MortgageConditionStatusThrough",
    #     through_fields=("mortgage", "offer_statuse"),
    #     related_name="mortgage",
    # )  

    # booking: fields.ManyToManyRelation["Booking"] = fields.ManyToManyField( # Entity
    #     model_name="models.Booking",
    #     related_name="mortgage_ticket",
    #     through="mortgage_ticket_booking_through",
    #     description="Сделка",
    #     null=True,
    #     on_delete=fields.CASCADE,
    #     backward_key="mortgage_ticket_id",
    #     forward_key="booking_id",
    # )

    # ticket_type: fields.ManyToManyRelation["MortgageTicketType"] = fields.ManyToManyField( # Entity
    #     model_name="models.MortgageTicketType",
    #     related_name="mortgage_ticket",
    #     through="mortgage_ticket_type_through",
    #     description="Типы ипотеки",
    #     null=True,
    #     on_delete=fields.CASCADE,
    #     backward_key="mortgage_ticket_id",
    #     forward_key="mortgage_ticket_type_id",
    # )

    created_at = models.DateTimeField(verbose_name="Дата и время создания", auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_ticket'
        verbose_name = "Заявка на ипотеку"
        verbose_name_plural = "21.2. Заявка на ипотеку"
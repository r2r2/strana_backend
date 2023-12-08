from datetime import datetime

from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageTicket(Model):
    """
    Ticket под ипотечный калькулятор.
    """
    id: int = fields.IntField(description="ID", pk=True)

    booking: fields.ManyToManyRelation["Booking"] = fields.ManyToManyField(  # Entity
        model_name="models.Booking",
        related_name="mortgage_ticket",
        through="mortgage_ticket_booking_through",
        description="Сделка",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_ticket_id",
        forward_key="booking_id",
    )

    ticket_type: fields.ManyToManyRelation["MortgageTicketType"] = fields.ManyToManyField(  # Entity
        model_name="models.MortgageTicketType",
        related_name="mortgage_ticket",
        through="mortgage_ticket_type_through",
        description="Типы ипотеки",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_ticket_id",
        forward_key="mortgage_ticket_type_id",
    )

    created_at: datetime = fields.DatetimeField(
        description="Дата и время создания", auto_now_add=True
    )

    class Meta:
        table = "mortgage_calculator_ticket"


class MortgageTicketBookingThrough(Model):
    """
    Отношение тикетов к сделкам
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgage_ticket_id: fields.ForeignKeyRelation[MortgageTicket] = fields.ForeignKeyField(
        model_name="models.MortgageTicket",
        related_name="mortgage_ticket_to_through",
        description="Тикет",
        on_delete=fields.CASCADE,
    )
    booking_id: fields.ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        model_name="models.Booking",
        related_name="booking_through",
        description="Сделка",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_calcutator_ticket_booking_through"


class MortgageTicketTypeThrough(Model):
    """
    Отношения Тикетов к типам
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgage_ticket_id: fields.ForeignKeyRelation[MortgageTicket] = fields.ForeignKeyField(
        model_name="models.MortgageTicket",
        related_name="mortgage_ticket_through",
        description="Тикет",
        on_delete=fields.CASCADE,
    )
    mortgage_type_id: fields.ForeignKeyRelation["MortgageTicketType"] = fields.ForeignKeyField(
        model_name="models.MortgageTicketType",
        related_name="ticket_type_through",
        description="Тип",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_calcutator_ticket_to_ticket_type_through"


class MortgageTicketRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий Ticket'ов под ипотечный калькулятор.

    """
    model = MortgageTicket

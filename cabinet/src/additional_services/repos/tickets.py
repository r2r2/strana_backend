from decimal import Decimal

from tortoise import fields

from common.orm.mixins import ReadWriteMixin

from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceTicket(BaseAdditionalServiceDatabaseModel):
    """
    Заявка на доп услуги
    """

    id: int = fields.IntField(description="ID", pk=True)
    service = fields.ForeignKeyField(
        model_name="models.AdditionalService",
        related_name="service_ticket",
        null=True,
        on_delete=fields.SET_NULL,
    )
    status = fields.ForeignKeyField(
        model_name="models.AmocrmStatus",
        related_name="amocrm_status",
        null=True,
        on_delete=fields.SET_NULL,
    )
    booking = fields.ForeignKeyField(
        model_name="models.Booking",
        related_name="booking_ticket",
        null=True,
        on_delete=fields.SET_NULL,
    )
    cost: Decimal | None = fields.DecimalField(
        description="Стоимость", decimal_places=2, max_digits=15, null=True
    )
    full_name: str = fields.CharField(max_length=150, description="ФИО клиента")
    phone: str = fields.CharField(
        max_length=20, description="Номер телефона", index=True
    )

    class Meta:
        table = "additional_services_ticket"


class AdditionalServiceTicketRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий заявки на доп услуги
    """

    model = AdditionalServiceTicket

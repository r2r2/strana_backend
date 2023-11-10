from decimal import Decimal

from tortoise import fields

from common.orm.mixins import ReadWriteMixin, CountMixin

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
    group_status = fields.ForeignKeyField(
        model_name="models.AdditionalServiceGroupStatus",
        related_name="service_group_status",
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
    user = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        related_name="tickets",
        null=True,
    )

    class Meta:
        table = "additional_services_ticket"


class AdditionalServiceTicketRepo(BaseAdditionalServiceRepo, ReadWriteMixin, CountMixin):
    """
    Репозиторий заявки на доп услуги
    """

    model = AdditionalServiceTicket

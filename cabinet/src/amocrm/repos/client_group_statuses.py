from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class ClientAmocrmGroupStatus(Model):
    """
    Модель Группирующих статусов для клиентов
    """
    id: int = fields.IntField(description='ID', pk=True)
    name: str = fields.CharField(max_length=150, description='Имя группирующего статуса', null=True)
    sort: int = fields.IntField(description='Приоритет', default=0)
    color: str = fields.CharField(max_length=40, description='Цвет', null=True)
    is_final: bool = fields.BooleanField(description="Завершающий статус", default=False)

    # Deprecated
    show_reservation_date: bool = fields.BooleanField(description="Выводить дату резерва", default=False)
    show_booking_date: bool = fields.BooleanField(description="Выводить дату брони", default=False)

    booking_tags: fields.ManyToManyRelation["BookingTag"]
    statuses: fields.ReverseRelation["AmocrmStatus"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "client_amocrm_group_statuses"


class ClientAmocrmGroupStatusRepo(BaseAmocrmRepo, GenericMixin):
    """
    Репозиторий Группирующих статусов
    """
    model = ClientAmocrmGroupStatus
    q_builder: orm.QBuilder = orm.QBuilder(ClientAmocrmGroupStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(ClientAmocrmGroupStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(ClientAmocrmGroupStatus)

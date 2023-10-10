from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class AmocrmGroupStatus(Model):
    """
    Модель Группирующих статусов
    """
    id: int = fields.IntField(description='ID', pk=True)
    name: str = fields.CharField(max_length=150, description='Имя группирующего статуса', null=True)
    sort: int = fields.IntField(description='Приоритет', default=0)
    color: str = fields.CharField(max_length=40, description='Цвет', null=True)
    is_final: bool = fields.BooleanField(description="Завершающий статус", default=False)

    # Deprecated
    show_reservation_date: bool = fields.BooleanField(description="Выводить дату резерва", default=False)
    show_booking_date: bool = fields.BooleanField(description="Выводить дату брони", default=False)

    amocrm_actions: fields.ManyToManyRelation["AmocrmAction"]
    booking_tags: fields.ManyToManyRelation["BookingTag"]
    statuses: fields.ReverseRelation["AmocrmStatus"]
    client_statuses: fields.ReverseRelation["AmocrmStatus"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "amocrm_group_statuses"


class AmocrmGroupStatusRepo(BaseAmocrmRepo, GenericMixin):
    """
    Репозиторий Группирующих статусов
    """
    model = AmocrmGroupStatus
    q_builder: orm.QBuilder = orm.QBuilder(AmocrmGroupStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AmocrmGroupStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AmocrmGroupStatus)

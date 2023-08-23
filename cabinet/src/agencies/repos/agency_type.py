from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseAgencyRepo


class AgencyGeneralType(Model):
    """
    Модель типа агентства (агрегатор/АН).
    """
    id: int = fields.IntField(description='ID', pk=True)
    sort: int = fields.IntField(default=0, description='Сортировка')
    slug: str = fields.CharField(max_length=20, description='Слаг', unique=True)
    label: str = fields.CharField(max_length=40, description='Название типа')

    def __repr__(self):
        return self.slug

    class Meta:
        table = "agencies_agency_general_type"
        ordering = ["sort"]


class AgencyGeneralTypeRepo(BaseAgencyRepo, GenericMixin):
    """
    Репозиторий типа агентства (агрегатор/АН).
    """
    model = AgencyGeneralType
    q_builder: orm.QBuilder = orm.QBuilder(AgencyGeneralType)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AgencyGeneralType)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AgencyGeneralType)

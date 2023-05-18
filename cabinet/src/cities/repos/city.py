from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseCityRepo


class City(Model):
    """
    Модель Города
    """
    name: str = fields.CharField(max_length=150)
    slug: str = fields.CharField(max_length=100)

    projects: fields.ReverseRelation["Project"]
    assign_clients: fields.ReverseRelation["AssignClientTemplate"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "cities_city"


class CityRepo(BaseCityRepo, CRUDMixin):
    """
    Репозиторий города
    """
    model = City

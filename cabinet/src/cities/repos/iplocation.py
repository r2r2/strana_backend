from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseCityRepo


class IPLocation(Model):
    """
    Модель IP адресов связанных с городом
    """
    ip_address: str = fields.CharField(verbose_name='IP адрес', null=False, max_length=15)
    city: fields.ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name='models.City', on_delete=fields.CASCADE, related_name="city",
        description='город', null=False
    )
    updated_at = fields.DatetimeField(auto_now=True, description='время создания/изменения записи', null=False)

    def __repr__(self):
        return f"{self.ip_address} from {self.city}"

    class Meta:
        table = "cities_iplocation"


class IPLocationRepo(BaseCityRepo, CRUDMixin):
    """
    Репозиторий города
    """
    model = IPLocation

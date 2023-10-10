from common.orm.mixins import ReadOnlyMixin
from tortoise import Model, fields

from ..entities import BaseCityRepo


class DaDataSettings(Model):
    """
    Модель настройки аdторизации в DaData
    """
    api_key: str = fields.TextField(description='API ключ', null=False)
    secret_key = fields.TextField(description='Секрет', null=False)

    class Meta:
        table = "cities_dadata_settings"


class DaDataSettingsRepo(BaseCityRepo, ReadOnlyMixin):
    """
    Репозиторий города
    """
    model = DaDataSettings

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from common.settings.entities import BaseSettingsRepo


class AddServiceSettings(Model):
    """
    Настройки доп. услуг
    """

    id: int = fields.IntField(description="ID", pk=True)
    email: str = fields.CharField(description="Email", max_length=100, null=True)

    class Meta:
        table = "settings_add_service_settings"


class AddServiceSettingsRepo(BaseSettingsRepo, CRUDMixin):
    """
    Репозиторий настроек доп. услуг
    """

    model = AddServiceSettings

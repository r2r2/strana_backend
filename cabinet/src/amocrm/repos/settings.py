from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseAmocrmRepo, BaseAmoCRMDatabaseModel


class AmoCRMSettings(BaseAmoCRMDatabaseModel):
    """
    Настройки AmoCRM
    """
    id: int = fields.IntField(description="ID", pk=True)
    client_id: str = fields.TextField(description="Client ID")
    client_secret: str = fields.TextField(description="Client Secret")
    access_token: str = fields.TextField(description="Access Token", null=True)
    refresh_token: str = fields.TextField(description="Refresh Token", null=True)
    redirect_uri = fields.CharField(max_length=255, description="Redirect URL")

    class Meta:
        table = "amocrm_amocrm_settings"


class AmoCRMSettingsRepo(BaseAmocrmRepo, ReadWriteMixin):
    """
    Репозиторий настроек AmoCRM
    """
    model: AmoCRMSettings = AmoCRMSettings

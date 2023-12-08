from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from common.settings.entities import BaseSettingsRepo


class SystemList(Model):
    """
    [Справочник] Список систем
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(description="Название", max_length=255, null=True)
    slug: str = fields.CharField(description="Слаг", max_length=255, null=True)

    taskchains: fields.ManyToManyRelation["TaskChain"]
    booking_tags: fields.ManyToManyRelation["BookingTag"]

    class Meta:
        table = "settings_system_list"


class SystemListRepo(BaseSettingsRepo, CRUDMixin):
    """
    Репозиторий настроек систем
    """
    model = SystemList

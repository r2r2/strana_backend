from tortoise import Model, fields

from common.models import TimeBasedMixin
from common.orm.mixins import CRUDMixin
from common.settings.entities import BaseSettingsRepo


class FeedbackSettings(Model, TimeBasedMixin):
    """
    Настройки форм обратной связи
    """

    id: int = fields.IntField(description="ID", pk=True)
    privilege_emails: fields.ReverseRelation["PrivilegeFeedbackEmail"]

    class Meta:
        table = "settings_feedback"


class FeedbackSettingsRepo(BaseSettingsRepo, CRUDMixin):
    """
    Репозиторий настроек форм обратной связи
    """

    model = FeedbackSettings

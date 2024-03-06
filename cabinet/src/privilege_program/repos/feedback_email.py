from datetime import datetime

from common.models import TimeBasedMixin
from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegeFeedbackEmail(Model, TimeBasedMixin):
    """
    Emails для результатов формы "Программа привилегий"
    """
    id: int = fields.IntField(pk=True, description="ID")
    full_name: str = fields.CharField(max_length=250, description="ФИО")
    email: str = fields.CharField(description="Email", max_length=250)
    feedback_settings = fields.ForeignKeyField(
        model_name="models.FeedbackSettings",
        related_name="privilege_emails",
        null=True,
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "privilege_feedback_email"

    def __repr__(self):
        return self.email


class PrivilegeFeedbackEmailRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Emails для результатов формы "Программа привилегий"
    """
    model = PrivilegeFeedbackEmail

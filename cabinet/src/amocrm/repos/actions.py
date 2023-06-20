from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class AmocrmAction(Model):
    """
    Модель действий в сделках
    """
    id: int = fields.IntField(description='ID', pk=True)
    name: str = fields.CharField(max_length=150, description='Название', null=True)
    role: fields.ForeignKeyNullableRelation["UserRole"] = fields.ForeignKeyField(
        description="Роль",
        model_name="models.UserRole",
        on_delete=fields.SET_NULL,
        related_name="role",
        null=True,
    )
    slug: str = fields.CharField(max_length=20, description='Код действия')
    group_statuses: fields.ManyToManyRelation["GroupAmocrmStatus"] = fields.ManyToManyField(
        description="Управляющие действия сделок",
        model_name="models.AmocrmGroupStatus",
        related_name="amocrm_actions",
        on_delete=fields.SET_NULL,
        through="amocrm_actions_group_statuses",
        backward_key="action_id",
        forward_key="group_status_id"
    )

    def __repr__(self):
        return self.name

    class Meta:
        table = "amocrm_actions"


class AmocrmActionRepo(BaseAmocrmRepo, ReadWriteMixin):
    """
    Репозиторий действий в сделках
    """
    model = AmocrmAction

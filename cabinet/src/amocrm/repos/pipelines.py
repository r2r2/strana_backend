from common.orm.mixins import CreateMixin, ListMixin, UpdateOrCreateMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class AmocrmPipeline(Model):
    """
    Модель Воронки
    """
    id: int = fields.IntField(verbose_name='ID воронки из amocrm', pk=True)
    name: str = fields.CharField(max_length=150, description='Название воронки')
    sort: int = fields.IntField(description='Приоритет', default=0)
    is_archive: bool = fields.BooleanField(description='В архиве', default=False)
    is_main: is_archive = fields.BooleanField(description='Основная воронка', default=False)
    account_id: int = fields.IntField(description='ID аккаунта', null=True)
    city: fields.ForeignKeyNullableRelation["City"] = fields.ForeignKeyField(
        description="Город", model_name="models.City", related_name="pipelines", null=True
    )

    def __repr__(self):
        return self.name

    class Meta:
        table = "amocrm_pipelines"


class AmocrmPipelineRepo(BaseAmocrmRepo, CreateMixin, UpdateOrCreateMixin, ListMixin):
    """
    Репозиторий воронки
    """
    model = AmocrmPipeline
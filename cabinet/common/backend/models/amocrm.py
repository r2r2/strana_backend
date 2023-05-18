from typing import Optional

from tortoise import Model, fields


class AmocrmPipelines(Model):
    """
    Table for interaction with amocrm pipelines.
    This is slave from backend, do not migrate!
    """

    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(description='Имя воронки', max_length=150)
    is_archive = fields.BooleanField(description='В архиве', default=False)
    is_main = fields.BooleanField(description='Является ли воронка главной', default=False)
    sort = fields.IntField(description='Сортировка', default=0)
    account_id = fields.IntField(description='ID аккаунта')

    city: Optional[int] = fields.OneToOneField('backend.BackendCity', null=True)
    city_id: Optional[int]

    class Meta:
        app = "backend"
        table = "amocrm_amocrmpipelines"

    def __str__(self):
        return f'<{self.id}:{self.name}>'


class AmocrmStatus(Model):
    """
    Table for interaction with amocrm statuses.
    Slave from backend, do not migrate!
    """

    id = fields.IntField(description='ID сделки из amocrm', pk=True)
    name = fields.CharField(description='Имя сделки', max_length=150)
    pipeline = fields.ForeignKeyField(
        model_name='backend.AmocrmPipelines', description='ID воронки из амо',
        on_delete=fields.CASCADE, related_name='statuses'
    )
    sort = fields.IntField(description='Сортировка', default=0)
    type = fields.IntField(
        default=0,
        description='Тип статуса',
    )

    pipeline_id: int

    def __str__(self):
        return f'<{self.id}:{self.name}>'

    class Meta:
        app = "backend"
        table = "amocrm_amocrmstatuses"

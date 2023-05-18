from tortoise import Model, fields

from .city import BackendCity


class BackendProject(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=200)
    slug: str = fields.CharField(max_length=50)
    amocrm_name: str = fields.CharField(max_length=200)
    amocrm_enum: str = fields.CharField(max_length=200)
    amocrm_organization: str = fields.CharField(max_length=200)
    amo_pipeline_id: str = fields.CharField(max_length=20)
    amo_responsible_user_id: str = fields.CharField(max_length=20)
    active: bool = fields.BooleanField()
    status: str = fields.CharField(description="Статус", max_length=20)

    city: fields.ForeignKeyRelation[BackendCity] = fields.ForeignKeyField("backend.BackendCity")
    city_id: int

    class Meta:
        app = "backend"
        table = "projects_project"

from tortoise import Model, fields

from common import cfields
from .city import BackendCity
from ..constaints import ProjectSkyColor


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
    address: str = fields.CharField(description="Адрес", max_length=250)
    transport_time = fields.IntField(description="Время в пути", null=True)
    project_color = fields.CharField(default="#FFFFFF", description="Цвет", max_length=8)
    title = fields.CharField(description="Заголовок", max_length=200, null=True)
    card_image = fields.CharField(description="Изображение на карточке", max_length=255, null=True)
    card_image_night = fields.CharField(description="Изображение на карточке (ночь)", max_length=255, null=True)
    card_sky_color: str = cfields.CharChoiceField(
        description="Цвет неба на карточке проекта",
        default=ProjectSkyColor.LIGHT_BLUE,
        choice_class=ProjectSkyColor,
        max_length=20,
    )
    min_flat_price = fields.IntField(description="Мин цена квартиры", null=True)
    min_flat_area = fields.DecimalField(description="Мин площадь квартиры", max_digits=7, decimal_places=2, null=True)
    max_flat_area = fields.DecimalField(description="Макс площадь квартиры", max_digits=7, decimal_places=2, null=True)

    city: fields.ForeignKeyRelation[BackendCity] = fields.ForeignKeyField("backend.BackendCity")
    metro: fields.ForeignKeyRelation["BackendMetro"] = fields.ForeignKeyField("backend.BackendMetro")
    transport: fields.ForeignKeyRelation["BackendTransport"] = fields.ForeignKeyField("backend.BackendTransport")

    city_id: int

    class Meta:
        app = "backend"
        table = "projects_project"

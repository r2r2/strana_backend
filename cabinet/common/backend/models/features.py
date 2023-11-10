from common import cfields
from common.backend.constaints import PropertyType
from common.backend.models import BackendCity


from tortoise import Model, fields


class BackendFeature(Model):
    """Модель особенности объекта собственности"""
    id: int = fields.IntField(pk=True)
    name = fields.CharField(description="Название", max_length=64)
    property_kind: str = cfields.CharChoiceField(
        description="Типы недвижимости",
        choice_class=PropertyType,
        max_length=64,
    )
    filter_show = fields.BooleanField(description="Отображать в фильтре листинга", default=True)
    main_filter_show = fields.BooleanField(description="Отображать в фильтре на главной", default=False)
    lot_page_show = fields.BooleanField(description="Отображать на странице лота", default=True)
    icon_show = fields.BooleanField(description="Отображать иконку", default=False)
    icon = fields.CharField(description="Иконка", max_length=255, null=True)
    icon_flats_show = fields.BooleanField(description="Отображать на странице flats", default=False)
    icon_hypo = fields.CharField(description="Картинка для тултипа в фильтре", max_length=255, null=True)
    icon_flats = fields.CharField(description="Иконка для страницы flats", max_length=255, null=True)
    description = fields.TextField(description="Описание", blank=True)
    order = fields.IntField(description="Очередность", default=0, db_index=True)
    is_button = fields.BooleanField(description="Выводить кнопкой", default=False)
    profit_id = fields.CharField(description="ID в Profitbase", max_length=64, null=True)
    city: fields.ManyToManyRelation["BackendCity"] = fields.ManyToManyField(
        model_name="backend.BackendCity",
        related_name="features",
        on_delete=fields.CASCADE,
        description="Город",
        through="properties_feature_cities",
        backward_key="feature_id",
        forward_key="city_id",
    )

    class Meta:
        app = "backend"
        table = "properties_feature"


class BackendFeatureCity(Model):
    id: int = fields.IntField(pk=True)
    feature: fields.ForeignKeyRelation[BackendFeature] = fields.ForeignKeyField(
        "backend.BackendFeature"
    )
    city: fields.ForeignKeyRelation[BackendCity] = fields.ForeignKeyField("backend.BackendCity")

    class Meta:
        app = "backend"
        table = "properties_feature_cities"

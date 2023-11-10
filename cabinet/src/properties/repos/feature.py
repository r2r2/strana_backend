from pydantic import Field
from typing import Any, Annotated

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields


class Feature(Model):
    """
    Особенность
    """
    id: int = fields.IntField(pk=True)
    backend_id: int = fields.IntField(unique=True)
    name = fields.CharField(description="Название", max_length=64)
    filter_show = fields.BooleanField(description="Отображать в фильтре листинга", default=True)
    main_filter_show = fields.BooleanField(description="Отображать в фильтре на главной", default=False)
    lot_page_show = fields.BooleanField(description="Отображать на странице лота", default=True)
    icon_show = fields.BooleanField(description="Отображать иконку", default=False)
    icon: Annotated[str, Field(max_length=255)] = cfields.MediaField(
        description="Иконка", max_length=255, null=True
    )
    icon_flats_show = fields.BooleanField(description="Отображать на странице flats", default=False)
    icon_hypo: Annotated[str, Field(max_length=255)] = cfields.MediaField(
        description="Картинка для тултипа в фильтре", max_length=255, null=True
    )
    icon_flats: Annotated[str, Field(max_length=255)] = cfields.MediaField(
        description="Иконка для страницы flats", max_length=255, null=True
    )
    description = fields.TextField(description="Описание", blank=True)
    order = fields.IntField(description="Очередность", default=0, db_index=True)
    is_button = fields.BooleanField(description="Выводить кнопкой", default=False)
    properties: fields.ManyToManyRelation["Property"] = fields.ManyToManyField(
        model_name="models.Property",
        related_name="property_features",
        on_delete=fields.CASCADE,
        description="Объект недвижимости",
        through="properties_feature_property_through",
        backward_key="feature_id",
        forward_key="property_id",
    )
    profit_id: str = fields.CharField(description="ID в Profitbase", max_length=64, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "properties_feature"


class FeatureRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий особенности
    """
    model = Feature

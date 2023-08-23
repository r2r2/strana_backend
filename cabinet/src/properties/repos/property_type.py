from common import orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BasePropertyRepo


class PropertyType(Model):
    """
    Модель типа объектов недвижимости.
    """
    id: int = fields.IntField(description='ID', pk=True)
    sort: int = fields.IntField(default=0, description='Приоритет')
    slug: str = fields.CharField(max_length=20, description='Слаг', unique=True)
    label: str = fields.CharField(max_length=40, description='Название типа')
    is_active: int = fields.BooleanField(default=True, description='Активность')
    pipelines: fields.ManyToManyRelation["AmocrmPipeline"] = fields.ManyToManyField(
        description="Воронки сделок",
        model_name='models.AmocrmPipeline',
        through="properties_property_type_pipelines",
        backward_key="property_type_id",
        forward_key="pipeline_id",
        related_name="property_type_pipelines",
    )

    def __repr__(self):
        return self.slug

    class Meta:
        table = "properties_property_type"
        ordering = ["sort"]


class PropertyTypeRepo(BasePropertyRepo, CRUDMixin):
    """
    Репозиторий типа объектов недвижимости.
    """
    model = PropertyType
    q_builder: orm.QBuilder = orm.QBuilder(PropertyType)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(PropertyType)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(PropertyType)

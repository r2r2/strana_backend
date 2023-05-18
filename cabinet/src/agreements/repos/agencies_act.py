from common import orm
from common.orm.mixins import CountMixin, CRUDMixin
from src.projects.repos import Project
from tortoise import fields

from ..entities import BaseAgreementRepo
from .base_agreement import BaseAgreement


class AgencyAct(BaseAgreement):
    """
    Акты агенства
    """
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        model_name="models.Project", description='Проект', on_delete=fields.SET_NULL, null=True,
    )
    created_by: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        description='Кем создано',
        on_delete=fields.CASCADE,
        related_name="created_acts",
        null=True,
    )
    updated_by: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        description='Кем изменено',
        on_delete=fields.CASCADE,
        related_name="updated_acts",
        null=True,
    )

    class Meta:
        table = "agencies_act"


class AgencyActRepo(BaseAgreementRepo, CRUDMixin, CountMixin):
    """
    Репозиторий актов
    """
    model = AgencyAct
    q_builder: orm.QBuilder = orm.QBuilder(AgencyAct)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AgencyAct)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AgencyAct)

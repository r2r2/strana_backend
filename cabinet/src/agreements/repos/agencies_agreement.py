from common import orm
from common.orm.mixins import CountMixin, CRUDMixin
from src.projects.repos import Project
from tortoise import fields

from ..entities import BaseAgreementRepo
from .agreement_type import AgreementType
from .base_agreement import BaseAgreement


class AgencyAgreement(BaseAgreement):
    """
    Договора агенства
    """
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        model_name="models.Project", description='Проект', on_delete=fields.CASCADE,
    )
    agreement_type: fields.ForeignKeyRelation[AgreementType] = fields.ForeignKeyField(
        model_name="models.AgreementType", description='Тип документа', on_delete=fields.CASCADE,
    )
    created_by: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        description='Кем создано',
        on_delete=fields.CASCADE,
        related_name="created_agreements",
        null=True,
    )
    updated_by: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        description='Кем изменено',
        on_delete=fields.CASCADE,
        related_name="updated_agreements",
        null=True,
    )

    class Meta:
        table = "agencies_agreement"


class AgencyAgreementRepo(BaseAgreementRepo, CRUDMixin, CountMixin):
    """
    Репозиторий договоров
    """
    model = AgencyAgreement
    q_builder: orm.QBuilder = orm.QBuilder(AgencyAgreement)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AgencyAgreement)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AgencyAgreement)

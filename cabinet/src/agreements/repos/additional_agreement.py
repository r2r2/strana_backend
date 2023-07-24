from datetime import datetime
from typing import Union

from common import cfields, orm
from common.models import TimeBasedMixin
from common.orm.mixins import CountMixin, CRUDMixin
from src.agencies.repos import Agency
from src.projects.repos import Project
from src.booking.repos import Booking
from tortoise import Model, fields

from ..entities import BaseAgreementRepo
from .additional_agreement_status import AdditionalAgreementStatus
from .additional_agreement_creating_data import AgencyAdditionalAgreementCreatingData


class AgencyAdditionalAgreement(Model, TimeBasedMixin):
    """
    Дополнительное соглашение к договору агентства.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    number: str = fields.CharField(description="Номер документа", max_length=50, null=True)
    status: fields.ForeignKeyRelation[AdditionalAgreementStatus] = fields.ForeignKeyField(
        model_name="models.AdditionalAgreementStatus", description="Статус", on_delete=fields.CASCADE, null=True,
    )
    template_name: str = fields.CharField(description="Название шаблона", max_length=200, null=True)
    agency: fields.ForeignKeyRelation[Agency] = fields.ForeignKeyField(
        model_name="models.Agency", description='Агенство', on_delete=fields.CASCADE, null=True,
    )
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        model_name="models.Project", description='Проект', on_delete=fields.CASCADE, null=True,
    )
    booking: fields.ForeignKeyRelation[Booking] = fields.ForeignKeyField(
        model_name="models.Booking", description='Бронь', on_delete=fields.SET_NULL, null=True,
    )
    reason_comment: str = fields.CharField(description="Комментарий (администратора)", max_length=300)
    signed_at: datetime = fields.DatetimeField(description="Когда подписано", null=True)
    files: Union[list, dict] = cfields.MutableDocumentContainerField(description="Файлы", null=True)
    creating_data: fields.ForeignKeyRelation[AgencyAdditionalAgreementCreatingData] = fields.ForeignKeyField(
        model_name="models.AgencyAdditionalAgreementCreatingData",
        description='Данные для формирования ДС (через админку)',
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        table = "agencies_additional_agreement"


class AgencyAdditionalAgreementRepo(BaseAgreementRepo, CRUDMixin, CountMixin):
    """
    Репозиторий дополнительных соглашений для договоров агентства.
    """

    model = AgencyAdditionalAgreement
    q_builder: orm.QBuilder = orm.QBuilder(AgencyAdditionalAgreement)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AgencyAdditionalAgreement)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AgencyAdditionalAgreement)

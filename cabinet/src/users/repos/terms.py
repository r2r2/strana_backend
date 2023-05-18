from typing import Optional
from uuid import UUID, uuid4

from common import cfields, mixins
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseUserRepo


class IsConType(mixins.Choices):
    YES = "yes", "Да"
    NO = "no", "Нет"
    SKIP = "skip", "Не важно"


class UniqueValueType(mixins.Choices):
    UNIQUE = "unique", "Уникален"
    NOT_UNIQUE = "not_unique", "Не уникален"
    CAN_DISPUTE = "can_dispute", "Закреплен, но можно оспорить"


class TermCity(Model):
    id: int = fields.IntField(pk=True)
    city = fields.ForeignKeyField(model_name="models.City")
    term = fields.ForeignKeyField(model_name="models.CheckTerm")

    class Meta:
        table = "users_checks_terms_cities"
        unique_together = (('city', 'term'),)


class TermPipeline(Model):
    id: int = fields.IntField(pk=True)
    pipeline = fields.ForeignKeyField(model_name="models.AmocrmPipeline")
    term = fields.ForeignKeyField(model_name="models.CheckTerm")

    class Meta:
        table = "users_checks_terms_pipelines"
        unique_together = (('pipeline', 'term'),)


class TermStatus(Model):
    id: int = fields.IntField(pk=True)
    status = fields.ForeignKeyField(model_name="models.AmocrmStatus")
    term = fields.ForeignKeyField(model_name="models.CheckTerm")

    class Meta:
        table = "users_checks_terms_statuses"
        unique_together = (('status', 'term'),)


class CheckTerm(Model):
    """
    Условия проверки на уникальность
    """
    uid: UUID = fields.UUIDField(description="ID", pk=True, default=uuid4)
    cities: list[str] = fields.ManyToManyField(description="Города", model_name='models.City',
                                               through="users_checks_terms_cities",
                                               backward_key="term_id", forward_key="city_id")
    pipelines: list[int] = fields.ManyToManyField(description="Воронки", model_name='models.AmocrmPipeline',
                                                  through="users_checks_terms_pipelines",
                                                  backward_key="term_id", forward_key="pipeline_id")
    statuses: list[int] = fields.ManyToManyField(description="Статусы", model_name='models.AmocrmStatus',
                                                 through="users_checks_terms_statuses",
                                                 backward_key="term_id", forward_key="status_id")
    is_agent: str = cfields.CharChoiceField(description="Есть агент", max_length=10,
                                            choice_class=IsConType, null=False)
    more_days: Optional[int] = fields.IntField(description="Больше скольки дней сделка находится в статусе", null=True)
    less_days: Optional[int] = fields.IntField(description="Меньше скольки дней сделка находится в статусе", null=True)
    is_assign_agency_status: str = cfields.CharChoiceField(description="Была ли сделка в статусе 'Фиксация за АН'",
                                                           choice_class=IsConType, max_length=10, null=False)
    priority: int = fields.IntField(description="Приоритет", null=False)
    unique_value: str = cfields.CharChoiceField(description="Статус уникальности", max_length=50,
                                                choice_class=UniqueValueType, null=False)

    class Meta:
        table = "users_checks_terms"
        ordering = ["priority"]


class CheckTermRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий условий проверки
    """
    model = CheckTerm

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
    assigned_to_agent: bool = fields.BooleanField(
        null=True,
        description="Закреплен за проверяющим агентом",
    )
    assigned_to_another_agent: bool = fields.BooleanField(
        null=True,
        description="Закреплен за другим агентом проверяющего агентства",
    )
    send_admin_email: bool = fields.BooleanField(
        default=False,
        description="Отправлять письмо администраторам при проверке клиента в данном статусе",
    )
    send_rop_email: bool = fields.BooleanField(
        default=False,
        description="Отправлять письмо РОПам при проверке клиента в данном статусе",
    )
    unique_status: fields.ForeignKeyNullableRelation["UniqueStatus"] = fields.ForeignKeyField(
        model_name="models.UniqueStatus",
        description="Статус уникальности",
        related_name="terms",
        null=True,
    )
    comment: str = fields.TextField(description="Комментарий", null=True)

    class Meta:
        table = "users_checks_terms"
        ordering = ["priority"]


class CheckTermRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий условий проверки
    """
    model = CheckTerm

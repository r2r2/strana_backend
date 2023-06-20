from tortoise import Model, fields

from common import cfields, mixins
from common.orm.mixins import CRUDMixin
from src.users.entities import BaseUserRepo


class PinningStatusType(mixins.Choices):
    """
    Статус закрепления
    """
    PINNED = "pinned", "Закреплен"
    NOT_PINNED = "not_pinned", "Не закреплен"
    PARTIALLY_PINNED = "partially_pinned", "Частично закреплен"


class PinningStatusCity(Model):
    """
    Модель городов - статусов закрепления
    """
    id: int = fields.IntField(description="ID", pk=True)
    city = fields.ForeignKeyField(model_name="models.City")
    pinning = fields.ForeignKeyField(model_name="models.PinningStatus")

    class Meta:
        table = "users_pinning_status_cities"
        unique_together = (('city', 'pinning'),)


class PinningStatusPipeline(Model):
    """
    Модель воронок - статусов закрепления
    """
    id: int = fields.IntField(description="ID", pk=True)
    pipeline = fields.ForeignKeyField(model_name="models.AmocrmPipeline")
    pinning = fields.ForeignKeyField(model_name="models.PinningStatus")

    class Meta:
        table = "users_pinning_status_pipelines"
        unique_together = (('pipeline', 'pinning'),)


class PinningStatusStatus(Model):
    """
    Модель AMO статусов - статусов закрепления
    """
    id: int = fields.IntField(description="ID", pk=True)
    status = fields.ForeignKeyField(model_name="models.AmocrmStatus")
    pinning = fields.ForeignKeyField(model_name="models.PinningStatus")

    class Meta:
        table = "users_pinning_status_statuses"
        unique_together = (('status', 'pinning'),)


class PinningStatus(Model):
    """
    Модель статусов закрепления
    """
    id: int = fields.IntField(description="ID", pk=True)
    cities: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        description="Города",
        model_name='models.City',
        through="users_pinning_status_cities",
        backward_key="pinning_id",
        forward_key="city_id",
        related_name="pinning_status_cities",
    )
    pipelines: fields.ManyToManyRelation["AmocrmPipeline"] = fields.ManyToManyField(
        description="Воронки",
        model_name='models.AmocrmPipeline',
        through="users_pinning_status_pipelines",
        backward_key="pinning_id",
        forward_key="pipeline_id",
        related_name="pinning_status_pipelines",
    )
    statuses: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        description="Статусы",
        model_name='models.AmocrmStatus',
        through="users_pinning_status_statuses",
        backward_key="pinning_id",
        forward_key="status_id",
        related_name="pinning_status_statuses",
    )
    priority: int = fields.IntField(description="Приоритет", null=False)
    result: str = cfields.CharChoiceField(
        description="Статус закрепления",
        max_length=36,
        choice_class=PinningStatusType,
    )

    class Meta:
        table = "users_pinning_status"
        ordering = ["priority"]


class PinningStatusRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий статусов закрепления
    """
    model = PinningStatus

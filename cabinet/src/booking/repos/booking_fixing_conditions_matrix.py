from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.amocrm.repos import AmocrmPipeline
from src.projects.repos import Project
from src.booking.constants import BookingCreatedSources
from src.booking.entities import BaseBookingRepo


class BookingFixingConditionsMatrixPipeline(Model):
    id: int = fields.IntField(pk=True)
    pipeline = fields.ForeignKeyField(
        model_name="models.AmocrmPipeline",
        on_delete=fields.CASCADE,
    )
    booking_fixing_conditions_matrix = fields.ForeignKeyField(
        model_name="models.BookingFixingConditionsMatrix",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "booking_fixing_conditions_matrix_pipeline_through"
        unique_together = (('pipeline', 'booking_fixing_conditions_matrix'),)


class BookingFixingConditionsMatrix(Model):
    """
    Матрица условий закрепления
    """

    id: int = fields.IntField(description="ID", pk=True)
    project: fields.ManyToManyRelation[Project] = fields.ManyToManyField(
        model_name="models.Project",
        related_name="booking_fixing_conditions_matrix",
        description="Проекты",
        null=True,
        through="booking_fixing_conditions_matrix_projects",
        on_delete=fields.CASCADE,
        backward_key="fixing_conditions_matrix_id",
        forward_key="project_id",
    )
    created_source: str = cfields.CharChoiceField(
        description="Источник создания онлайн-бронирования",
        null=True,
        max_length=100,
        choice_class=BookingCreatedSources,
    )
    consultation_type: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="models.ConsultationType",
        related_name='fixing_conditions',
        null=True,
        on_delete=fields.SET_NULL,
        description="Тип консультации",
    )

    status_on_create: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="models.AmocrmGroupStatus",
        related_name='fixing_conditions',
        null=True,
        on_delete=fields.SET_NULL,
        description="Статус создаваемой сделки",
    )
    pipelines: fields.ManyToManyRelation[AmocrmPipeline] = fields.ManyToManyField(
        description="Воронки",
        model_name='models.AmocrmPipeline',
        through="booking_fixing_conditions_matrix_pipeline_through",
        backward_key="booking_fixing_conditions_matrix_id",
        forward_key="pipeline_id",
    )
    amo_responsible_user_id: str | None = fields.CharField(
        description="ID ответственного в AmoCRM", max_length=200, null=True
    )

    priority: int = fields.IntField(description="Приоритет", null=False, default=0)

    class Meta:
        table = "booking_fixing_conditions_matrix"
        ordering = ["priority"]


class BookingFixingConditionsMatrixProjects(Model):
    """
    Матрица условий закрепления
    """

    id: int = fields.IntField(description="ID", pk=True)
    fixing_conditions_matrix: fields.ForeignKeyRelation[BookingFixingConditionsMatrix] = fields.ForeignKeyField(
        model_name="models.BookingFixingConditionsMatrix",
        on_delete=fields.CASCADE,
        description="Матрица условий закрепления",
        related_name="booking_project_matrix",
    )
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        model_name="models.Project",
        on_delete=fields.CASCADE,
        description="Проект",
        related_name="booking_fixing_condition_matrix",
    )

    class Meta:
        table = "booking_fixing_conditions_matrix_projects"


class BookingFixingConditionsMatrixRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозиторий матрицы условий закрепления
    """
    model: BookingFixingConditionsMatrix = BookingFixingConditionsMatrix

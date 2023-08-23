from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.projects.repos import Project
from src.booking.constants import BookingCreatedSources
from src.booking.entities import BaseBookingRepo


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
    status_on_create: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="models.AmocrmGroupStatus", related_name='fixing_conditions', null=True, on_delete=fields.SET_NULL,
        description="Статус создаваемой сделки",
    )

    class Meta:
        table = "booking_fixing_conditions_matrix"


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

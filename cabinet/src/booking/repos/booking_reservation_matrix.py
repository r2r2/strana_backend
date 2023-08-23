from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin
from src.projects.repos import Project
from src.booking.constants import BookingCreatedSources
from src.booking.entities import BaseBookingRepo


class BookingReservationMatrix(Model):
    """
    Матрица сроков резервирования
    """

    id: int = fields.IntField(description="ID", pk=True)
    project: fields.ManyToManyRelation[Project] = fields.ManyToManyField(
        model_name="models.Project",
        related_name="booking_reservation_matrix",
        description="Проекты",
        null=True,
        through="booking_reservation_matrix_projects",
        on_delete=fields.CASCADE,
        backward_key="reservation_matrix_id",
        forward_key="project_id",
    )
    created_source: str = cfields.CharChoiceField(
        description="Источник создания онлайн-бронирования",
        null=True,
        max_length=100,
        choice_class=BookingCreatedSources,
    )
    reservation_time: float = fields.FloatField(description="Время резервирования квартир (ч)", null=True)

    class Meta:
        table = "booking_reservation_matrix"


class BookingReservationMatrixProjects(Model):
    """
    Матрица сроков резервирования
    """

    id: int = fields.IntField(description="ID", pk=True)
    reservation_matrix: fields.ForeignKeyRelation[BookingReservationMatrix] = fields.ForeignKeyField(
        model_name="models.BookingReservationMatrix",
        on_delete=fields.CASCADE,
        description="Матрица сроков резервирования",
        related_name="booking_reservation_matrix_projects",
    )
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        model_name="models.Project",
        on_delete=fields.CASCADE,
        description="Проект",
        related_name="booking_reservation_matrix_projects",
    )

    class Meta:
        table = "booking_reservation_matrix_projects"


class BookingReservationMatrixRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозиторий матрицы сроков резервирования
    """
    model: BookingReservationMatrix = BookingReservationMatrix

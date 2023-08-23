from typing import Any, Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import cfields, orm
from common.orm.mixins import CountMixin, CRUDMixin, FacetsMixin
from ..entities import BaseProjectRepo
from ..constants import ProjectStatus, ProjectSkyColor


class Project(Model):
    """
    Проект
    """
    id: int = fields.IntField(description="ID", pk=True)
    slug: Optional[str] = fields.CharField(description="Слаг", max_length=100, null=True)
    global_id: Optional[str] = fields.CharField(
        description="Глобальный ID", max_length=200, unique=True, null=True
    )
    name: Optional[str] = fields.CharField(description="Имя", max_length=200, null=True)
    city: ForeignKeyNullableRelation["City"] = fields.ForeignKeyField(
        "models.City", related_name="projects", null=True, on_delete=fields.SET_NULL,
    )
    address: str = fields.CharField(description="Адрес", max_length=250)
    metro: fields.ForeignKeyRelation["Metro"] = fields.ForeignKeyField(
        "models.Metro", on_delete=fields.SET_NULL, null=True
    )
    transport: fields.ForeignKeyRelation["Transport"] = fields.ForeignKeyField(
        "models.Transport", on_delete=fields.SET_NULL, null=True
    )
    transport_time = fields.IntField(description="Время в пути", null=True)
    project_color = fields.CharField(default="#FFFFFF", description="Цвет", null=True, max_length=8)
    title = fields.CharField(description="Заголовок", max_length=200, null=True)
    card_image = cfields.MediaField(description="Изображение на карточке", max_length=255, null=True)
    card_image_night = cfields.MediaField(description="Изображение на карточке (ночь)", max_length=255, null=True)
    card_sky_color: str = cfields.CharChoiceField(
        description="Цвет неба на карточке проекта",
        default=ProjectSkyColor.LIGHT_BLUE,
        choice_class=ProjectSkyColor,
        max_length=20,
    )
    min_flat_price = fields.IntField(description="Мин цена квартиры", null=True)
    min_flat_area = fields.DecimalField(description="Мин площадь квартиры", max_digits=7, decimal_places=2, null=True)
    max_flat_area = fields.DecimalField(description="Макс площадь квартиры", max_digits=7, decimal_places=2, null=True)

    amocrm_name: Optional[str] = fields.CharField(
        description="Имя AmoCRM", max_length=200, null=True
    )
    amocrm_enum: Optional[int] = fields.BigIntField(description="Enum в AmoCRM", null=True)
    amocrm_organization: Optional[str] = fields.CharField(
        description="Организация в AmoCRM", max_length=200, null=True
    )
    amo_pipeline_id: Optional[str] = fields.CharField(
        description="ID воронки в AmoCRM", max_length=200, null=True
    )
    amo_responsible_user_id: Optional[str] = fields.CharField(
        description="ID ответственного в AmoCRM", max_length=200, null=True
    )
    is_active: bool = fields.BooleanField(description="Активный", default=True)
    priority: int = fields.IntField(description="Приоритет вывода", null=True)
    status: str = cfields.CharChoiceField(
        description="Статус", max_length=200, default=ProjectStatus.CURRENT, choice_class=ProjectStatus
    )
    show_in_paid_booking: bool = fields.BooleanField(description="Отображать в платном бронировании", default=True)
    discount: int = fields.SmallIntField(description="Скидка в %", default=0)

    booking_reservation_matrix: fields.ManyToManyRelation["BookingReservationMatrix"]
    booking_fixing_conditions_matrix: fields.ManyToManyRelation["BookingFixingConditionsMatrix"]

    @property
    def flat_area_range(self) -> dict[str, fields.DecimalField]:
        return dict(min=self.min_flat_area, max=self.max_flat_area)

    @property
    def card_image_display(self):
        # доработка изменение размера изображения
        if self.card_image:
            return self.card_image

    @property
    def card_image_night_display(self):
        # доработка изменение размера изображения
        if self.card_image_night:
            return self.card_image_night

    def __str__(self) -> str:
        if self.name:
            return self.name
        return str(self.id)

    class Meta:
        table = "projects_project"
        ordering = ["priority"]


class ProjectRepo(BaseProjectRepo, CRUDMixin, CountMixin, FacetsMixin):
    """
    Репозиторий проекта
    """
    model = Project
    q_builder: orm.QBuilder = orm.QBuilder(Project)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Project)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Project)

    async def update_or_create(self, filters: dict[str, Any], data: dict[str, Any]) -> Project:
        """
        Создание или обновление проекта
        """
        if not data.get('amocrm_enum'):
            data['amocrm_enum'] = 0
        project, _ = await Project.update_or_create(**filters, defaults=data)
        return project

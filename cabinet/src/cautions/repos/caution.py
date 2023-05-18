from typing import Union

from common import cfields, orm
from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation, ForeignKeyRelation

from common.orm.mixins import GenericMixin, ExecuteMixin
from src.users.constants import CautionType
from src.cautions.entities import BaseCautionRepo


class Caution(Model):
    """Предупреждение, выводимые пользователям"""
    id: int = fields.IntField(description="ID", pk=True, index=True)

    is_active: bool = fields.BooleanField(description="Активное", default=False)
    type: str = cfields.CharChoiceField(
        description="Тип", max_length=20, default=CautionType.INFORMATION, choice_class=CautionType, null=True
    )
    roles: Union[list, dict] = fields.JSONField(description="Доступно ролям", null=True)
    text = fields.TextField(description="Выводимый текст", default="")
    priority = fields.IntField(description="Приоритет вывода")

    expires_at = fields.DatetimeField(description="Активен до", null=True)
    created_at = fields.DatetimeField(description="Когда создано", null=True)  # default = current_time
    updated_at = fields.DatetimeField(description="Когда обновлено", null=True)

    created_by: ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        description="Кем создано",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        null=True,
        related_name="cautions_created"
    )
    update_by: ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        description="Кем обновлено",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        null=True,
        related_name="cautions_updated"
    )

    class Meta:
        table = "cautions_caution"


class CautionMute(Model):
    """Таблица связи тех, кого уже уведомили предупреждением"""

    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        null=True,
    )
    caution: ForeignKeyRelation["Caution"] = fields.ForeignKeyField(
        description="Предупреждение",
        model_name="models.Caution",
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        table = "users_caution_mute"
        unique_together = (
            ("user_id", "caution_id")
        )


class CautionMuteRepo(BaseCautionRepo, GenericMixin):
    """
    Репозиторий предупреждений
    """
    model = CautionMute
    q_builder: orm.QBuilder = orm.QBuilder(CautionMute)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(CautionMute)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(CautionMute)


class CautionRepo(BaseCautionRepo, GenericMixin, ExecuteMixin):
    """
    Репозиторий предупреждений
    """
    model = Caution
    q_builder: orm.QBuilder = orm.QBuilder(Caution)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Caution)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Caution)

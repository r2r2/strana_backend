from tortoise import Model, fields

from common import cfields, mixins
from common.orm.mixins import CRUDMixin
from src.users.entities import BaseUserRepo


class IconType(mixins.Choices):
    """
    Тип иконки
    """
    ICON = "icon", "Иконка"
    IMAGE = "image", "Изображение"
    WARNING = "warning", "Предупреждение"
    CHECK_SOLUTION = "checkSolution", "Решение"
    DOT = "dot", "Точка"
    NOT_PINNED = "notPinned", "Не закреплено"


class StyleListType(mixins.Choices):
    """
    Стиль в списке
    """
    DEFAULT = "default", "По умолчанию"
    PRIMARY = "primary", "Основной"
    SUCCESS = "success", "Успешный"
    INFO = "info", "Информационный"
    WARNING = "warning", "Предупреждение"
    DANGER = "danger", "Опасный"
    SECONDARY = "secondary", "Второстепенный"
    LIGHT = "light", "Светлый"
    DARK = "dark", "Темный"
    WHITE = "white", "Белый"
    TRANSPARENT = "transparent", "Прозрачный"


class StatusType(mixins.Choices):
    """
    Тип статуса
    """
    PINNING = "pinning", "Статус закрепления"
    UNIQUE = "unique", "Статус уникальности"


class UniqueStatus(Model):
    """
    Таблица статусов уникальности/закрепления
    """
    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(description="Заголовок", max_length=255)
    subtitle: str = fields.CharField(description="Подзаголовок", max_length=255, null=True)
    icon: str = cfields.CharChoiceField(
        description="Иконка",
        max_length=36,
        choice_class=IconType,
    )
    color: str = fields.CharField(default="#8F00FF", description="Цвет текста", max_length=7, null=True)
    background_color: str = fields.CharField(default="#8F00FF", description="Цвет фона", max_length=7, null=True)
    border_color: str = fields.CharField(default="#8F00FF", description="Цвет границы", max_length=7, null=True)
    slug: str = fields.CharField(description="Слаг", max_length=255, null=True)
    style_list: str = cfields.CharChoiceField(
        description="Стиль в списке",
        max_length=36,
        choice_class=StyleListType,
        null=True,
    )
    type: str = cfields.CharChoiceField(
        description="Тип",
        max_length=36,
        choice_class=StatusType,
        null=True,
    )
    comment: str = fields.TextField(description="Комментарий", null=True)
    can_dispute: bool = fields.BooleanField(default=False, description="Можно оспорить статус клиента")
    stop_check: bool = fields.BooleanField(default=False, description="Остановить проверку")

    terms: fields.ReverseRelation["CheckTerm"]
    pinning_status: fields.ReverseRelation["PinningStatus"]
    users_pinning_status: fields.ReverseRelation["UserPinningStatus"]
    checks_history: fields.ReverseRelation["CheckHistory"]
    checks: fields.ReverseRelation["Check"]

    class Meta:
        table = "users_unique_statuses"


class UniqueStatusRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий статусов уникальности
    """
    model = UniqueStatus

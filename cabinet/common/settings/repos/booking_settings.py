from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from common.settings.entities import BaseSettingsRepo


class BookingSettings(Model):
    """
    Настройки бронирования
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(description="Название", max_length=255, null=True)
    default_flats_reserv_time: float = fields.FloatField(
        description="Время резервирования квартир по умолчанию (ч)",
        default=24,
        null=True,
    )
    created_at: str = fields.DatetimeField(auto_now_add=True, description="Дата создания")
    updated_at: str = fields.DatetimeField(auto_now=True, description="Дата обновления")

    class Meta:
        table = "settings_booking_settings"


class BookingSettingsRepo(BaseSettingsRepo, CRUDMixin):
    """
    Репозиторий настроек бронирования
    """
    model = BookingSettings

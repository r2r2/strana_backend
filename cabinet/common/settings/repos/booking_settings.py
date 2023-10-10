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
    lifetime: int = fields.FloatField(description="Время жизни сделки, дней", null=True)
    updated_lifetime: int = fields.FloatField(
        description="Время жизни сделки после продления в амо, дней", null=True
    )
    extension_deadline = fields.FloatField(
        description="Дедлайн продления сделки до закрытия, дней", null=True
    )
    max_extension_number: int = fields.IntField(
        description="Количество попыток продления", null=True
    )
    pay_extension_number: int = fields.IntField(
        description="Сколько раз при неудачной оплате добавляем дополнительное время клиенту",
        default=1,
    )
    pay_extension_value: int = fields.IntField(
        description="Сколько минут добавляем клиенту при неудачной оплате (мин)",
        default=10,
    )
    created_at: str = fields.DatetimeField(
        auto_now_add=True, description="Дата создания"
    )
    updated_at: str = fields.DatetimeField(auto_now=True, description="Дата обновления")

    class Meta:
        table = "settings_booking_settings"


class BookingSettingsRepo(BaseSettingsRepo, CRUDMixin):
    """
    Репозиторий настроек бронирования
    """

    model = BookingSettings

from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseCityRepo


class City(Model):
    """
    Модель Города
    """
    id: int
    name: str = fields.CharField(max_length=150)
    slug: str = fields.CharField(max_length=100)
    short_name: str = fields.CharField(max_length=50, null=True, description="Короткое название")
    users = fields.ManyToManyField(
        model_name="models.User",
        on_delete=fields.SET_NULL,
        null=True,
        through="users_cities",
        related_name="users_cities",
        forward_key="user_id",
        backward_key="city_id",
        description="Пользователи",
    )
    color: str = fields.CharField(default="#FFFFFF", max_length=8, description="Цвет")
    global_id: str = fields.CharField(max_length=50, description="ID из портала", null=True)

    projects: fields.ReverseRelation["Project"]
    assign_clients: fields.ReverseRelation["AssignClientTemplate"]

    pinning_status_cities: fields.ManyToManyRelation["PinningStatus"]
    tickets: fields.ManyToManyRelation["Ticket"]
    blocks: fields.ManyToManyRelation["Block"]
    links: fields.ManyToManyRelation["Link"]
    elements: fields.ManyToManyRelation["Element"]
    metro_line: fields.ForeignKeyRelation["MetroLine"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "cities_city"


class MetroLine(Model):
    """
    Модель линии метро
    """
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=255, description="Название")
    color: str = fields.CharField(default="#FF0000", max_length=8, description="Цвет")
    city = fields.ForeignKeyField(
        "models.City", null=True, on_delete=fields.CASCADE, related_name="metro_line"
    )

    metro: fields.ForeignKeyRelation["BackendMetro"]

    class Meta:
        table = "cities_metroline"


class Metro(Model):
    """
    Модель метро
    """
    id: int = fields.IntField(pk=True)
    name = fields.CharField(description="Название", max_length=32)
    latitude = fields.DecimalField(description="Широта", decimal_places=6, max_digits=9, null=True)
    longitude = fields.DecimalField(description="Долгота", decimal_places=6, max_digits=9, null=True)
    line = fields.ForeignKeyField("models.MetroLine", null=True, on_delete=fields.CASCADE, related_name="metro")
    order = fields.IntField(description="Порядок", default=0, index=True)

    class Meta:
        table = "cities_metro"


class Transport(Model):
    """
    Способ передвижения
    """
    id: int
    name = fields.CharField(description="Название", max_length=100)
    icon = fields.CharField(description="Иконка", max_length=255, null=True, blank=True)
    icon_content = fields.TextField(description="Контент иконки", null=True, blank=True)

    class Meta:
        table = "cities_transport"


class CityRepo(BaseCityRepo, CRUDMixin):
    """
    Репозиторий города
    """
    model = City


class MetroLineRepo(BaseCityRepo, CRUDMixin):
    """
    Репозиторий линии метро
    """
    model = MetroLine


class MetroRepo(BaseCityRepo, CRUDMixin):
    """
    Репозиторий метро
    """
    model = Metro


class TransportRepo(BaseCityRepo, CRUDMixin):
    """
    Репозиторий транспорта
    """
    model = Transport

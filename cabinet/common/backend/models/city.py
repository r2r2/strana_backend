from tortoise import Model, fields


class BackendCity(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=150)
    slug: str = fields.CharField(max_length=100)
    active: bool = fields.BooleanField()
    color: str = fields.TextField(default="#FFFFFF", description="Цвет")

    metro_line: fields.ForeignKeyRelation["BackendMetroLine"]

    class Meta:
        app = "backend"
        table = "cities_city"


class BackendMetroLine(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=255, description="Название")
    color: str = fields.TextField(default="#FF0000", description="Цвет")
    city = fields.ForeignKeyField(
        "backend.BackendCity", null=True, on_delete=fields.CASCADE, related_name="metro_line"
    )

    metro: fields.ForeignKeyRelation["BackendMetro"]

    class Meta:
        app = "backend"
        table = "cities_metroline"


class BackendMetro(Model):
    id: int = fields.IntField(pk=True)
    name = fields.CharField(description="Название", max_length=32)
    latitude = fields.DecimalField(description="Широта", decimal_places=6, max_digits=9, null=True)
    longitude = fields.DecimalField(description="Долгота", decimal_places=6, max_digits=9, null=True)
    line = fields.ForeignKeyField("backend.BackendMetroLine", null=True, on_delete=fields.CASCADE, related_name="metro")
    order = fields.IntField(description="Порядок", default=0, index=True)

    class Meta:
        app = "backend"
        table = "cities_metro"


class BackendTransport(Model):
    """
    Способ передвижения
    """
    name = fields.CharField(description="Название", max_length=100)
    icon = fields.CharField(description="Иконка", max_length=255, null=True, blank=True)
    icon_content = fields.TextField(description="Контент иконки", null=True, blank=True)

    class Meta:
        app = "backend"
        table = "cities_transport"

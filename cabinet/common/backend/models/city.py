from tortoise import Model, fields


class BackendCity(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=150)
    slug: str = fields.CharField(max_length=100)
    active: bool = fields.BooleanField()

    class Meta:
        app = "backend"
        table = "cities_city"

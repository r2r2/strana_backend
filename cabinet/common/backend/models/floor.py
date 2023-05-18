from tortoise import Model, fields

from .sections import BackendSection


class BackendFloor(Model):
    id: int = fields.IntField(pk=True)
    number: int = fields.IntField()

    section: fields.ForeignKeyNullableRelation[BackendSection] = fields.ForeignKeyField(
        "backend.BackendSection", null=True, on_delete=fields.CASCADE
    )
    section_id: int

    class Meta:
        app = "backend"
        table = "buildings_floor"

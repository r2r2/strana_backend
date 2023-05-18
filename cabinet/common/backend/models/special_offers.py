from tortoise import Model, fields

from .properties import BackendProperty


class BackendSpecialOffer(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=200)
    is_active: bool = fields.BooleanField()

    class Meta:
        app = "backend"
        table = "properties_specialoffer"


class BackendSpecialOfferProperty(Model):
    id: int = fields.IntField(pk=True)
    specialoffer: fields.ForeignKeyRelation[BackendSpecialOffer] = fields.ForeignKeyField(
        "backend.BackendSpecialOffer"
    )
    property: fields.ForeignKeyRelation[BackendProperty] = fields.ForeignKeyField("backend.BackendProperty")

    class Meta:
        app = "backend"
        table = "properties_specialoffer_properties"

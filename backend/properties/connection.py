from graphene import Connection, Boolean
from common.graphene import ExtendedConnection
from .constants import PropertyType

class AllLayoutConnection(ExtendedConnection):
    class Meta:
        abstract = True

    with_commercial = Boolean()
    with_flat = Boolean()
    with_commercial_apartment = Boolean()

    def resolve_with_commercial(self, info, **kwargs):
        return self.iterable.filter(type=PropertyType.COMMERCIAL).exists()

    def resolve_with_flat(self, info, **kwargs):
        return self.iterable.filter(type=PropertyType.FLAT).exists()

    def resolve_with_commercial_apartment(self, info, **kwargs):
        return self.iterable.filter(type=PropertyType.COMMERCIAL_APARTMENT).exists()
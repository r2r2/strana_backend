import factory
from random import randrange
from django.contrib.sites.models import Site
from cities.models import City, MetroLine, Metro, Transport, Map


class SiteFactory(factory.DjangoModelFactory):
    domain = factory.Sequence(lambda n: f"example{n}.com")
    name = factory.Sequence(lambda n: f"example{n}.com")

    class Meta:
        model = Site


class MapFactory(factory.DjangoModelFactory):
    slug = factory.Sequence(lambda n: f"Map_{n}")

    class Meta:
        model = Map


class CityFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Город {n}")
    site = factory.SubFactory(SiteFactory)
    order = factory.Sequence(lambda n: n)
    local_coords = factory.Sequence(
        lambda n: f"{randrange(0, 100)}.{randrange(0, 100)},{randrange(0, 100)}.{randrange(0, 100)}"
    )
    map = factory.SubFactory(MapFactory)

    class Meta:
        model = City


class MetroLineFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Линия метро {n}")
    city = factory.SubFactory(CityFactory)

    class Meta:
        model = MetroLine


class MetroFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Станция метро {n}")
    line = factory.SubFactory(MetroLineFactory)

    class Meta:
        model = Metro


class TransportFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Способ передвижения {n}")

    class Meta:
        model = Transport

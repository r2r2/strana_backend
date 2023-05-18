import factory
from contacts.models import Office, Subdivision, Social


class OfficeFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Office {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Office


class SubdivisionFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Subdivision {n}")

    class Meta:
        model = Subdivision


class SocialFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Social {n}")
    link = factory.Sequence(lambda n: f"https://example{n}.com")
    order = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = Social

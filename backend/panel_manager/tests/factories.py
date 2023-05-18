import datetime
import factory
from factory import fuzzy
from pytz import UTC

from ..models import Manager, Meeting, Client, Statistic


class ManagerFactory(factory.DjangoModelFactory):
    login = factory.Sequence(lambda n: "+7903{:07}".format(n))

    user = factory.SubFactory("users.tests.factories.UserFactory")

    class Meta:
        model = Manager


class ClientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Client


class MeetingFactory(factory.DjangoModelFactory):
    client = factory.SubFactory(ClientFactory)
    manager = factory.SubFactory(ManagerFactory)

    class Meta:
        model = Meeting


class StatisticFactory(factory.DjangoModelFactory):
    metting = factory.SubFactory(MeetingFactory)
    view = fuzzy.FuzzyInteger(low=0, high=10)
    time = fuzzy.FuzzyDateTime(
        datetime.datetime(2021, 1, 1, tzinfo=UTC),
        datetime.datetime(2021, 7, 1, tzinfo=UTC),
        force_day=3,
        force_second=42,
    )

    class Meta:
        model = Statistic

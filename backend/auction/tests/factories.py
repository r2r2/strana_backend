import pytz
import factory
from factory.django import DjangoModelFactory
from django.conf import settings

from ..models import Auction


class AuctionFactory(DjangoModelFactory):
    is_active = True
    start = factory.Faker(
        "date_time_between",
        start_date="-5d",
        end_date="-20d",
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )
    end = factory.Faker(
        "date_time_between",
        start_date="+5d",
        end_date="+20d",
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )
    property_object = factory.SubFactory("properties.tests.factories.PropertyFactory")

    class Meta:
        model = Auction

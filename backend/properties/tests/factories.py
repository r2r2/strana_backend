from random import choice
from random import randint as R
from random import randrange

import factory
import pytz
from django.conf import settings

from properties.constants import PropertyCardKind, PropertyType
from properties.models import *

from ..constants import FeatureType


class PropertyFactory(factory.DjangoModelFactory):
    number = factory.Sequence(lambda n: str(n))
    article = factory.Sequence(lambda n: f"article-{n}")
    area = factory.Faker("pydecimal", left_digits=3, right_digits=2)
    price = factory.Faker("pydecimal", left_digits=9, right_digits=2)
    plan = factory.django.FileField(
        data=b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"/>'
    )
    planoplan = factory.Faker("uri")
    project = factory.SubFactory("projects.tests.factories.ProjectFactory")
    building = factory.SubFactory("buildings.tests.factories.BuildingFactory")

    class Meta:
        model = Property

    @factory.post_generation
    def purposes(self, create, extracted):
        if not create:
            return
        if extracted:
            for pr in extracted:
                self.purposes.add(pr)

    @factory.post_generation
    def special_offers(self, create, extracted):
        if not create:
            return
        if extracted:
            for o in extracted:
                self.specialoffer_set.add(o)


class FlatFactory(PropertyFactory):
    type = PropertyType.FLAT
    rooms = factory.Faker("pyint", min_value=0, max_value=4, step=1)

    class Meta:
        model = Property


class ParkingPlaceFactory(PropertyFactory):
    type = PropertyType.PARKING

    class Meta:
        model = Property


class CommercialPremiseFactory(PropertyFactory):
    type = PropertyType.COMMERCIAL

    class Meta:
        model = Property


class CommercialApartmentFactory(PropertyFactory):
    type = PropertyType.COMMERCIAL_APARTMENT

    class Meta:
        model = Property


class FurnishFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Furnish {n}")
    description = factory.Faker("text")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Furnish


class FurnishImageFactory(factory.DjangoModelFactory):
    file = factory.django.ImageField()
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = FurnishImage


class FurnishPointFactory(factory.DjangoModelFactory):
    point = f"{R(1, 9)}{R(1, 9)}.{R(1, 9)}{R(1, 9)},{R(1, 9)}{R(1, 9)}.{R(1, 9)}{R(1, 9)}"
    text = factory.Faker("text")

    class Meta:
        model = FurnishPoint


class FlatRoomsMenuFactory(factory.DjangoModelFactory):
    rooms_0_image = factory.django.ImageField()
    rooms_0_text = factory.Faker("text")

    class Meta:
        model = FlatRoomsMenu


class PropertyCardFactory(factory.DjangoModelFactory):
    uptitle = factory.Faker("word")
    title = factory.Faker("word")
    text = factory.Faker("word")
    image = factory.django.ImageField()
    kind = PropertyCardKind.ANOTHER

    class Meta:
        model = PropertyCard


class WindowViewTypeFactory(factory.DjangoModelFactory):
    title = factory.Faker("word")
    building = factory.SubFactory("buildings.tests.factories.BuildingFactory")
    section = factory.SubFactory("buildings.tests.factories.SectionFactory")

    class Meta:
        model = WindowViewType


class WindowViewFactory(factory.DjangoModelFactory):
    type = factory.SubFactory(WindowViewTypeFactory)
    order = factory.Sequence(lambda n: n)
    ppoi = f"{randrange(0, 100)},{randrange(0,100)}"

    class Meta:
        model = WindowView


class WindowViewAngleFactory(factory.DjangoModelFactory):
    angle = randrange(1, 360)
    window_view = factory.SubFactory(WindowViewFactory)

    class Meta:
        model = WindowViewAngle


class MiniPlanPointFactory(WindowViewFactory):
    class Meta:
        model = MiniPlanPoint


class MiniPlanPointAngleFactory(factory.DjangoModelFactory):
    angle = randrange(1, 360)
    mini_plan = factory.SubFactory(MiniPlanPointFactory)

    class Meta:
        model = MiniPlanPointAngle


class LayoutFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"AL-{n}")

    class Meta:
        model = Layout

    @factory.post_generation
    def property_set(self, create, extracted):
        if not create:
            return
        if extracted:
            for p in extracted:
                self.property_set.add(p)


class FeatureFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"feature {n}")
    filter_show = True
    icon = factory.django.ImageField()
    icon_show = True
    description = factory.Faker("text")
    order = factory.Sequence(lambda n: n)
    kind = choice(FeatureType.choices)[0]

    class Meta:
        model = Feature


class SpecialOfferFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"offer {n}")
    start_date = factory.Faker(
        "date_time_between",
        start_date="-5d",
        end_date="-20d",
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )
    finish_date = factory.Faker(
        "date_time_between",
        start_date="+5d",
        end_date="+20d",
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )
    is_active = True
    is_display = True

    class Meta:
        model = SpecialOffer


class PropertyPurposeFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"purpose {n}")
    icon = factory.django.ImageField()
    description = factory.Faker("text")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = PropertyPurpose


class ListingActionFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"action {n}")
    image = factory.django.ImageField()
    description = factory.Faker("text")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = ListingAction

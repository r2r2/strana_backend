import factory
from ..models import (
    CommercialPropertyPage,
    CommercialPropertyPageAdvantage,
    CommercialPropertyPageSlide,
    Tenant,
)


class TenantFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"tenant {n}")

    class Meta:
        model = Tenant


class CommercialPropertyPageFactory(factory.DjangoModelFactory):
    class Meta:
        model = CommercialPropertyPage


class CommercialPropertyPageAdvantageFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Advantage {n}")

    class Meta:
        model = CommercialPropertyPageAdvantage


class CommercialPropertyPageSlideFactory(factory.DjangoModelFactory):
    image = factory.django.ImageField()
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = CommercialPropertyPageSlide

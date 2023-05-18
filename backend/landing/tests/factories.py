import random
import factory
from factory import DjangoModelFactory
from ..constants import LandingBlockChoices
from ..models import *


class LandingFactory(DjangoModelFactory):
    slug = factory.Sequence(lambda n: f"landing-{n}")
    is_promo = False
    title = factory.Faker("word")
    text = factory.Faker("text")
    main_image = factory.django.ImageField()
    card_image = factory.django.ImageField()

    class Meta:
        model = Landing


class LandingBlockFactory(DjangoModelFactory):
    landing = factory.SubFactory(LandingFactory)
    title = factory.Sequence(lambda n: f"block {n}")
    text = factory.Faker("text")
    anchor = factory.Sequence(lambda n: f"#block-{n}")
    block_type = random.choice(LandingBlockChoices.choices)[0]
    image_1 = factory.django.ImageField()
    image_2 = factory.django.ImageField()
    image_3 = factory.django.ImageField()
    presentation = factory.django.FileField()
    send_to_email = True

    class Meta:
        model = LandingBlock

    @factory.post_generation
    def furnishes(self, create, extracted):
        if not create:
            return
        if extracted:
            for f in extracted:
                self.furnishes.add(f)

    @factory.post_generation
    def progress_set(self, create, extracted):
        if not create:
            return
        if extracted:
            for p in extracted:
                self.progress_set.add(p)


class SliderBlockSlideFactory(DjangoModelFactory):
    file = factory.django.ImageField()
    block = factory.SubFactory(LandingBlockFactory)

    class Meta:
        model = SliderBlockSlide


class TwoColumnsBlockItemFactory(DjangoModelFactory):
    file = factory.django.ImageField()
    block = factory.SubFactory(LandingBlockFactory)

    class Meta:
        model = TwoColumnsBlockItem


class DigitsBlockItemFactory(DjangoModelFactory):
    title = factory.Faker("sentence")
    block = factory.SubFactory(LandingBlockFactory)

    class Meta:
        model = DigitsBlockItem


class StepsBlockItemFactory(DjangoModelFactory):
    title = factory.Faker("sentence")
    block = factory.SubFactory(LandingBlockFactory)

    class Meta:
        model = StepsBlockItem


class AdvantageBlockItemFactory(DjangoModelFactory):
    file = factory.django.ImageField()
    subtitle = factory.Faker("sentence")
    block = factory.SubFactory(LandingBlockFactory)

    class Meta:
        model = AdvantageBlockItem


class ListBlockItemFactory(DjangoModelFactory):
    title = factory.Faker("sentence")
    block = factory.SubFactory(LandingBlockFactory)

    class Meta:
        model = ListBlockItem

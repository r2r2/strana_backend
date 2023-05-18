import factory
from ..models import (
    MainPage,
    MainPageSlide,
    MainPageIdeologyCard,
    MapText,
    MainPageStory,
    MainPageStoryImage,
)


class MainPageFactory(factory.DjangoModelFactory):
    site_id = 1
    news_title = factory.Faker("word")
    news_image = factory.django.ImageField()

    class Meta:
        model = MainPage


class MainPageSlideFactory(factory.DjangoModelFactory):
    title = factory.Faker("word")
    text = factory.Faker("text")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = MainPageSlide


class MainPageIdeologyCardFactory(factory.DjangoModelFactory):
    title = factory.Faker("word")
    text = factory.Faker("text")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = MainPageIdeologyCard


class MapTextFactory(factory.DjangoModelFactory):
    text = factory.Faker("text")

    class Meta:
        model = MapText


class MainPageStoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"story {n}")
    page = factory.SubFactory(MainPageFactory)
    file = factory.django.ImageField()

    class Meta:
        model = MainPageStory


class MainPageStoryImageFactory(factory.DjangoModelFactory):

    story = factory.SubFactory(MainPageStoryFactory)

    class Meta:
        model = MainPageStoryImage

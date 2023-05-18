import factory
from ..models import News, NewsSlide, MassMedia, NewsForm


class NewsSlideFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Image title {n}")
    image = factory.django.ImageField()
    video = factory.django.FileField()

    class Meta:
        model = NewsSlide


class NewsFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"News {n + 1}")
    slug = factory.Sequence(lambda n: f"news-{n + 1}")
    intro = factory.Sequence(lambda n: f"News {n + 1} intro")
    text = factory.Sequence(lambda n: f"News {n + 1} text")
    published = True
    form = factory.SubFactory("news.tests.factories.NewsFormFactory")

    class Meta:
        model = News


class MassMediaFactory(factory.DjangoModelFactory):
    name = factory.Faker("word")
    logo = factory.django.FileField()

    class Meta:
        model = MassMedia


class NewsFormFactory(factory.DjangoModelFactory):
    title = factory.Faker("word")

    class Meta:
        model = NewsForm

import factory

from projects.constants import ProjectStatusType
from projects.models import (
    ProjectGallerySlide,
    ProjectAdvantage,
    Project,
    ProjectIdeology,
    ProjectIdeologyCard,
    ProjectAdvantageSlide,
    ProjectWebcam,
    ProjectLabel,
)


class ProjectFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Project {n + 1}")
    slug = factory.Sequence(lambda n: f"project-{n + 1}")
    latitude = factory.Faker("pydecimal", left_digits=2, right_digits=6)
    longitude = factory.Faker("pydecimal", left_digits=2, right_digits=6)
    address = factory.Faker("text")
    description = factory.Faker("text")
    order = factory.Sequence(lambda n: n)
    plan = factory.django.ImageField(width=100, height=100, color=0)
    active = True
    status = ProjectStatusType.CURRENT

    class Meta:
        model = Project


class ProjectGallerySlideFactory(factory.DjangoModelFactory):
    image = factory.django.ImageField()
    order = factory.Sequence(lambda n: n)
    video = factory.django.FileField()
    video_mobile = factory.django.FileField()

    class Meta:
        model = ProjectGallerySlide


class ProjectAdvantageFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Заголовок преимущества {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = ProjectAdvantage


class ProjectAdvantageSlideFactory(factory.DjangoModelFactory):
    image = factory.django.ImageField()
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = ProjectAdvantageSlide


class ProjectIdeologyCardFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Заголовок крточки идеологии {n}")
    text = factory.Faker("text")
    file = factory.django.ImageField()
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = ProjectIdeologyCard


class ProjectIdeologyFactory(factory.DjangoModelFactory):
    text_1 = factory.Faker("text")
    text_2 = factory.Faker("text")

    class Meta:
        model = ProjectIdeology


class ProjectWebcamFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f"Веб-камера {n}")
    order = factory.Sequence(lambda n: n)
    link = factory.Faker("url")

    class Meta:
        model = ProjectWebcam


class ProjectLabelFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Лейбл {n}")
    file = factory.django.ImageField()
    description = factory.Sequence(lambda n: f"Описание лейбла {n}")

    class Meta:
        model = ProjectLabel

    @factory.post_generation
    def projects(self, create, extracted):
        if not create:
            return
        if extracted:
            for proj in extracted:
                self.projects.add(proj)

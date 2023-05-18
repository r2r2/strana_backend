import factory
from infras.models import (
    Infra,
    InfraCategory,
    InfraContent,
    MainInfra,
    MainInfraContent,
    SubInfra,
    RoundInfra,
)


class InfraCategoryFactory(factory.DjangoModelFactory):
    order = factory.Sequence(int)
    name = factory.Sequence(lambda n: f"Infra Category {n + 1}")
    icon = factory.django.FileField()

    class Meta:
        model = InfraCategory


class InfraFactory(factory.DjangoModelFactory):
    project = factory.SubFactory("projects.factories.ProjectFactory")
    category = factory.SubFactory(InfraCategoryFactory)
    name = factory.Sequence(lambda n: f"Infra {n + 1}")

    class Meta:
        model = Infra


class InfraContentFactory(factory.DjangoModelFactory):
    name = factory.Faker("word")
    value = factory.Faker("word")
    infra = factory.SubFactory(InfraFactory)

    class Meta:
        model = InfraContent


class MainInfraFactory(factory.DjangoModelFactory):
    project = factory.SubFactory("projects.factories.ProjectFactory")
    name = factory.Faker("word")

    class Meta:
        model = MainInfra


class MainInfraContentFactory(factory.DjangoModelFactory):
    name = factory.Faker("word")
    value = factory.Faker("word")
    main_infra = factory.SubFactory(MainInfraFactory)

    class Meta:
        model = MainInfraContent


class SubInfraFactory(factory.DjangoModelFactory):
    project = factory.SubFactory("projects.factories.ProjectFactory")
    name = factory.Faker("word")

    class Meta:
        model = SubInfra


class RoundInfraFactory(factory.DjangoModelFactory):
    project = factory.SubFactory("projects.factories.ProjectFactory")
    name = factory.Faker("word")

    class Meta:
        model = RoundInfra

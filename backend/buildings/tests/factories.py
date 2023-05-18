import factory
from buildings.models import Building, Section, Floor


class BuildingFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Building {n}")
    number = factory.Sequence(lambda n: str(n + 1))
    building_state = (Building.STATE_UNFINISHED,)
    built_year = factory.Sequence(lambda n: 2019 + n)
    ready_quarter = factory.Sequence(lambda n: n % 4 + 1)
    plan = factory.django.ImageField()
    window_view_plan = factory.django.ImageField()
    project = factory.SubFactory("projects.tests.factories.ProjectFactory")
    finish_date = factory.Faker("future_date")

    class Meta:
        model = Building


class SectionFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Section {n}")
    number = factory.Sequence(lambda n: n)
    plan = factory.django.ImageField(width=100, height=100, color=0)
    building = factory.SubFactory(BuildingFactory)

    class Meta:
        model = Section


class FloorFactory(factory.DjangoModelFactory):
    number = factory.Sequence(lambda n: n + 1)
    plan = factory.django.FileField(
        data=b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"/>'
    )
    section = factory.SubFactory(SectionFactory)
    plan_width = 1200
    plan_height = 1920

    class Meta:
        model = Floor

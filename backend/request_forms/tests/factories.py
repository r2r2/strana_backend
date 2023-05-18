import factory
from ..constants import RequestType
from ..models import Manager, CustomForm, CustomFormEmployee


class ManagerFactory(factory.DjangoModelFactory):
    name = factory.Faker("name")
    email = factory.Faker("email")
    type_list = RequestType.values

    class Meta:
        model = Manager


class CustomFormFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Form {n}")
    active = True

    class Meta:
        model = CustomForm


class CustomFormEmployeeFactory(factory.DjangoModelFactory):
    full_name = factory.Sequence(lambda n: f"employee {n}")
    form = factory.SubFactory(CustomFormFactory)
    city = factory.SubFactory("cities.tests.factories.CityFactory")
    project = factory.SubFactory("projects.tests.factories.ProjectFactory")
    is_for_main_page = False

    class Meta:
        model = CustomFormEmployee

import random
import factory
from datetime import datetime, timedelta, timezone
from company.models import (
    Document,
    DocumentCategory,
    PartnersPage,
    PartnersPageBlock,
    Vacancy,
    VacancyCategory,
    VacancyPage,
    VacancyPageAdvantage,
    VacancyPageForm,
    IdeologySlider,
    IdeologyCard,
    AboutPage,
    LargeTenant,
    Person,
    Story,
    StoryImage,
    CompanyValue,
)
from ..constants import PersonCategory


class DocumentCategoryFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Заголовок категории {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = DocumentCategory


class DocumentFactory(factory.DjangoModelFactory):
    date = factory.Sequence(lambda n: datetime.now(tz=timezone.utc) - timedelta(days=n))
    title = factory.Sequence(lambda n: f"Заголовок {n}")
    file = factory.django.FileField()

    class Meta:
        model = Document


class PartnersPageBlockFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Блок {n}")

    class Meta:
        model = PartnersPageBlock


class PartnersPageFactory(factory.DjangoModelFactory):
    text_1 = factory.Sequence(lambda n: "Страница партнерам")

    class Meta:
        model = PartnersPage


class VacancyFactory(factory.DjangoModelFactory):
    job_title = factory.Sequence(lambda n: f"Должность {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Vacancy


class VacancyCategoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Категория {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = VacancyCategory


class VacancyPageFactory(factory.DjangoModelFactory):
    text_1 = factory.Sequence(lambda n: "Страница вакансий")

    class Meta:
        model = VacancyPage


class VacancyPageAdvantageFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Преимущество {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = VacancyPageAdvantage


class VacancyPageFormFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Заголовок формы {n}")

    class Meta:
        model = VacancyPageForm


class AboutPageFactory(factory.DjangoModelFactory):
    text_1 = factory.Faker("text")
    text_2 = factory.Faker("text")
    offices = factory.Sequence(lambda n: n + 1)
    description = factory.Faker("sentence")
    image = factory.django.ImageField()
    ideology_description = factory.Faker("sentence")
    ideology_text = factory.Faker("text")
    ideology_image_one = factory.django.ImageField()
    ideology_image_two = factory.django.ImageField()

    class Meta:
        model = AboutPage


class IdeologyCardFactory(factory.DjangoModelFactory):
    title = factory.Faker("word")
    text = factory.Faker("text")
    image = factory.django.ImageField()
    order = factory.Sequence(lambda n: n + 1)
    about_section = factory.SubFactory(AboutPageFactory)

    class Meta:
        model = IdeologyCard


class IdeologySliderFactory(factory.DjangoModelFactory):
    text = factory.Faker("text")
    image = factory.django.ImageField()
    order = factory.Sequence(lambda n: n + 1)
    about_section = factory.SubFactory(AboutPageFactory)

    class Meta:
        model = IdeologySlider


class LargeTenantFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"tenant {n}")

    class Meta:
        model = LargeTenant


class PersonFactory(factory.DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    bio = factory.Faker("text")
    category = random.choice(PersonCategory.choices)
    image = factory.django.ImageField()

    class Meta:
        model = Person


class StoryFactory(factory.DjangoModelFactory):
    about_section = factory.SubFactory(AboutPageFactory)
    name = factory.Faker("word")
    order = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = Story


class StoryImageFactory(factory.DjangoModelFactory):
    story = factory.SubFactory(StoryFactory)
    order = factory.Sequence(lambda n: n + 1)
    text = factory.Faker("text")

    class Meta:
        model = StoryImage


class CompanyValueFactory(factory.DjangoModelFactory):
    about_section = factory.SubFactory(AboutPageFactory)
    name = factory.Faker("word")
    text = factory.Faker("text")
    order = factory.Sequence(lambda n: n + 1)
    file = factory.django.ImageField()

    class Meta:
        model = CompanyValue

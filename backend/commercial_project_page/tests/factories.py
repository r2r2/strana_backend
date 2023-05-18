import factory

from ..models import *


class CommercialProjectPageFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"comm project page {n}")
    project = factory.SubFactory("projects.tests.factories.ProjectFactory")

    class Meta:
        model = CommercialProjectPage


class ProjectAudienceFactory(factory.DjangoModelFactory):
    commercial_project_page = factory.SubFactory(CommercialProjectPageFactory)

    class Meta:
        model = ProjectAudience


class CommercialProjectGallerySlideFactory(factory.DjangoModelFactory):
    commercial_project_page = factory.SubFactory(CommercialProjectPageFactory)

    class Meta:
        model = CommercialProjectGallerySlide


class CommercialInvestCardFactory(factory.DjangoModelFactory):
    class Meta:
        model = CommercialInvestCard


class AudienceIncomeFactory(factory.DjangoModelFactory):
    audience = factory.SubFactory(ProjectAudienceFactory)
    income = 5_000

    class Meta:
        model = AudienceIncome


class AudienceFactFactory(factory.DjangoModelFactory):
    audience = factory.SubFactory(ProjectAudienceFactory)

    class Meta:
        model = AudienceFact


class AudienceAgeFactory(factory.DjangoModelFactory):
    audience = factory.SubFactory(ProjectAudienceFactory)
    percent = 10

    class Meta:
        model = AudienceAge


class CommercialProjectComparisonFactory(factory.DjangoModelFactory):
    commercial_project_page = factory.SubFactory(CommercialProjectPageFactory)

    class Meta:
        model = CommercialProjectComparison


class CommercialProjectComparisonItemFactory(factory.DjangoModelFactory):
    comparison = factory.SubFactory(CommercialProjectComparisonFactory)

    class Meta:
        model = CommercialProjectComparisonItem

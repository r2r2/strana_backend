import factory
from purchase.models import PurchaseType, PurchaseTypeStep, PurchaseTypeCategory


class PurchaseTypeCategoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Категория покупки {n}")
    order = factory.Sequence(lambda n: n)
    slug = factory.Sequence(lambda n: f"category_{n}")

    class Meta:
        model = PurchaseTypeCategory


class PurchaseTypeFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Способ покупки {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = PurchaseType


class PurchaseTypeStepFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Шаг {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = PurchaseTypeStep

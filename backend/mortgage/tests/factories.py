import factory
from decimal import Decimal

from ..models import (
    Bank,
    MortgageAdvantage,
    MortgageInstrument,
    MortgagePage,
    Offer,
    Program,
    MortgagePageForm,
)


class MortgagePageFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Title {n}")

    class Meta:
        model = MortgagePage


class MortgagePageFormFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Заголовок формы {n}")

    class Meta:
        model = MortgagePageForm


class MortgageAdvantageFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Advantage title {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = MortgageAdvantage


class MortgageInstrumentFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Instrument title {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = MortgageInstrument


class BankFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Банк {n}")
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Bank


class OfferFactory(factory.DjangoModelFactory):
    deposit = factory.Sequence(lambda n: (Decimal(n % 30), Decimal(n % 70 + 30)))
    rate = factory.Sequence(lambda n: (Decimal(n % 10), Decimal(n % 20 + 10)))
    term = factory.Sequence(lambda n: (Decimal(n % 10), Decimal(n % 20 + 10)))
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Offer

    @factory.post_generation
    def projects(self, create, extracted):
        if not create:
            return
        if extracted:
            for proj in extracted:
                self.projects.add(proj)


class ProgramFactory(factory.DjangoModelFactory):
    name = factory.Faker("sentence", nb_words=2)
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Program

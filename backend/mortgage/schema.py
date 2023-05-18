from decimal import Decimal, InvalidOperation
from graphene import ObjectType, Field, Node, String, ID, List, Int, Float
from django.db.models import Prefetch
from graphene_django import DjangoConnectionField, DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django_optimizer import OptimizedDjangoObjectType, query
from graphql_relay import from_global_id
from common.graphene import ExtendedConnection
from common.schema import FacetFilterField, FacetWithCountType, SpecType, MultiImageObjectTypeMeta
from .filters import OfferFilterSet
from .models import (
    Bank,
    MortgageAdvantage,
    MortgageInstrument,
    MortgagePage,
    Offer,
    OfferTypeStep,
    OfferFAQ,
    OfferPanel,
    Program,
    MortgagePageForm,
    MortgagePageFormEmployee,
)


class MortgagePageType(OptimizedDjangoObjectType):
    """
    Тип страницы ипотеки
    """

    title = String()

    @staticmethod
    def resolve_title(obj, info, **kwargs):
        min_value = getattr(obj, "min_value")
        title = getattr(obj, "title")
        formattable_title = getattr(obj, "formattable_title")
        if min_value is not None and formattable_title and formattable_title.count("{"):
            return formattable_title.format(min_value)
        return title

    class Meta:
        model = MortgagePage


class MortgageAdvantageType(OptimizedDjangoObjectType):
    """
    Тип преимущества на странице ипотеки
    """

    title = String()

    @staticmethod
    def resolve_title(obj, info, **kwargs):
        min_value = getattr(obj, "min_value")
        title = getattr(obj, "title")
        formattable_title = getattr(obj, "formattable_title")
        if min_value is not None and formattable_title and formattable_title.count("{"):
            return formattable_title.format(min_value)
        return title

    class Meta:
        model = MortgageAdvantage


class MortgageInstrumentType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип ипотечного инструмента
    """

    class Meta:
        model = MortgageInstrument


class MortgagePageFormType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип формы на странице ипотеки
    """

    class Meta:
        model = MortgagePageForm


class MortgagePageFormEmployeeType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип сатрудника формы на странице ипотеки
    """

    class Meta:
        model = MortgagePageFormEmployee


class ProgramType(OptimizedDjangoObjectType):
    """
    Тип ипотечной програмы
    """

    class Meta:
        model = Program
        interfaces = (Node,)


class OfferTypeStepGraphene(OptimizedDjangoObjectType):
    """
    Тип шага способа покупки
    """

    class Meta:
        model = OfferTypeStep
        interfaces = (Node,)


class OfferFAQGraphene(OptimizedDjangoObjectType):
    """
    FAQ
    """

    class Meta:
        model = OfferFAQ
        interfaces = (Node,)


class OfferType(OptimizedDjangoObjectType):
    offertypestep_set = DjangoListField(OfferTypeStepGraphene)
    faq = DjangoListField(OfferFAQGraphene)
    min_deposit = Int()
    min_rate = Float()
    max_term = Int()
    min_subs_rate = Float()
    max_subs_term = Int()

    payment = Int()
    subs_payment = Int()
    min_amount = Int()
    max_amount = Int()

    class Meta:
        model = Offer
        interfaces = (Node,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False
        filterset_class = OfferFilterSet
        exclude = ("is_active", "projects", "deposit", "rate", "term")

    @staticmethod
    def resolve_min_amount(obj, info, **kwargs):
        if obj.amount:
            return obj.amount.lower

    @staticmethod
    def resolve_max_amount(obj, info, **kwargs):
        if obj.amount:
            return obj.amount.upper

    @staticmethod
    def resolve_min_deposit(obj, info, **kwargs):
        if obj.deposit:
            return obj.deposit.lower

    @staticmethod
    def resolve_min_rate(obj, info, **kwargs):
        if obj.rate:
            return obj.rate.lower

    @staticmethod
    def resolve_max_term(obj, info, **kwargs):
        if obj.term:
            return obj.term.upper

    @staticmethod
    def resolve_min_subs_rate(obj, info, **kwargs):
        if obj.subs_rate:
            return obj.subs_rate.lower

    @staticmethod
    def resolve_max_subs_term(obj, info, **kwargs):
        if obj.subs_term:
            return obj.subs_term.upper


class OfferPanelType(OptimizedDjangoObjectType):
    min_deposit = Int()
    min_rate = Float()
    max_term = Int()
    min_subs_rate = Float()
    max_subs_term = Int()

    payment = Int()
    subs_payment = Int()

    class Meta:
        model = OfferPanel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = False
        filterset_class = OfferFilterSet
        exclude = ("is_active", "projects", "deposit", "rate", "term", "amount")

    @staticmethod
    def resolve_min_deposit(obj, info, **kwargs):
        if obj.deposit:
            return obj.deposit.lower

    @staticmethod
    def resolve_min_rate(obj, info, **kwargs):
        if obj.rate:
            return obj.rate.lower

    @staticmethod
    def resolve_max_term(obj, info, **kwargs):
        if obj.term:
            return obj.term.upper

    @staticmethod
    def resolve_min_subs_rate(obj, info, **kwargs):
        if obj.subs_rate:
            return obj.subs_rate.lower

    @staticmethod
    def resolve_max_subs_term(obj, info, **kwargs):
        if obj.subs_term:
            return obj.subs_term.upper


class BankType(OptimizedDjangoObjectType):
    """
    Тип банка
    """

    offer_panel_set = DjangoConnectionField(OfferPanelType)

    min_rate = Float()
    max_term = Float()
    min_subs_rate = Float()
    max_subs_term = Int()

    payment = Int()
    subs_payment = Int()

    class Meta:
        model = Bank
        interfaces = (Node,)
        connection_class = ExtendedConnection

    @staticmethod
    def resolve_offer_set(obj, info, **kwargs):
        return getattr(obj, "offer_set").all()[:1]


class MortgageQuery(ObjectType):
    """
    Запросы ипотек
    """

    all_offers = DjangoFilterConnectionField(
        OfferType, description="Фильтр по ипотечным предложениям"
    )
    all_banks = DjangoConnectionField(
        BankType,
        mortgage_type=String(),
        city=ID(),
        program=ID(),
        project=List(ID),
        price=Float(),
        deposit=Float(),
        deposit_sum=Int(),
        term=Int(),
        order_by=String(),
        description="Фильтр по банкам",
    )

    all_offers_facets = FacetFilterField(
        FacetWithCountType,
        filtered_type=OfferType,
        filterset_class=OfferFilterSet,
        method_name="facets",
        description="Фасеты для фильтра по ипотечным предложениям",
    )
    all_offers_specs = FacetFilterField(
        List(SpecType),
        filtered_type=OfferType,
        filterset_class=OfferFilterSet,
        method_name="specs",
        description="Спеки для фильтра по ипотечным предложениям",
    )
    mortgage_page = Field(MortgagePageType, city=ID(), description="Страница ипотеки")
    mortgage_forms_employee = List(
        MortgagePageFormEmployeeType, city=ID(), description="Сотрудники форм страницы ипотеки"
    )

    @staticmethod
    def resolve_mortgage_page(self, info, **kwargs):
        city_id = kwargs.get("city", None)
        if city_id:
            _, city = from_global_id(city_id)
            return query(MortgagePage.objects.filter(site__city=city), info).first()
        current_site = info.context.site
        return query(MortgagePage.objects.filter(site=current_site.id), info).first()

    @staticmethod
    def resolve_all_offers(obj, info, **kwargs):
        queryset = Offer.objects.filter(is_active=True)
        if "price" in kwargs and "term" in kwargs and "deposit" in kwargs:
            try:
                price = Decimal(kwargs["price"])
                deposit = Decimal(kwargs["deposit"])
                term = float(kwargs["term"])
                queryset = queryset.annotate_payment(price, deposit, term)
            except (ValueError, InvalidOperation):
                pass
        return query(queryset, info)

    @staticmethod
    def resolve_all_banks(obj, info, **kwargs):
        kwargs["type"] = kwargs.get("mortgage_type")
        offer_qs = OfferFilterSet(kwargs, OfferPanel.objects.filter(is_active=True).order_by("rate")).qs
        queryset = Bank.objects.filter(offerpanel__id__in=offer_qs).distinct()
        if "price" in kwargs and "term" in kwargs and "deposit" in kwargs:
            try:
                price = Decimal(kwargs["price"])
                deposit = Decimal(kwargs["deposit"])
                term = float(kwargs["term"])
                offer_qs = offer_qs.annotate_payment(price, deposit, term)
                queryset = queryset.annotate_payment(price, deposit, term, offer_qs)
                if "payment" == kwargs.get("order_by"):
                    offer_qs = offer_qs.order_by("payment")
                    queryset = queryset.order_by("payment")
            except (ValueError, InvalidOperation):
                pass
        return query(
            queryset.annotate_min_rate(offer_qs)
            .annotate_max_term(offer_qs)
            .prefetch_related(Prefetch("offerpanel_set", queryset=offer_qs.select_related("program"))),
            info,
        )

    @staticmethod
    def resolve_mortgage_forms_employee(obj, info, **kwargs):
        qs = MortgagePageFormEmployee.objects.all()
        if kwargs.get("city"):
            try:
                _, city_id = from_global_id(kwargs.get("city"))
                return query(qs.filter(city=city_id), info)
            except (UnicodeDecodeError, BinasciiError, ValueError):
                return None
        return query(qs, info)

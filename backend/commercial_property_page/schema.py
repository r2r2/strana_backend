from binascii import Error as BinasciiError
from graphene import ObjectType, Field, ID, List, Int, Float, String
from graphene_django_optimizer import query, OptimizedDjangoObjectType
from graphql_relay import from_global_id
from common.schema import FacetFilterField, MultiImageObjectTypeMeta, RangeType, SpecType
from properties.constants import PropertyType
from properties.models import Property, Furnish
from .filters import CommercialPropertyPageFilterSet
from .models import (
    CommercialPropertyPageAdvantage,
    CommercialPropertyPage,
    CommercialPropertyPageSlide,
    Tenant,
    CommercialRentForm,
    CommercialRentFormEmployee,
)


class CommercialPropertyPageAdvantageType(
    OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta
):
    """
    Тип преимущества на странице коммерческой недвижимости
    """

    class Meta:
        model = CommercialPropertyPageAdvantage
        exclude = ("file", "page")


class CommercialPropertyPageSlideType(
    OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta
):
    """
    Тип слайда страницы коммерческой недвижимости
    """

    class Meta:
        model = CommercialPropertyPageSlide
        exclude = ("image", "page")


class TenantType(OptimizedDjangoObjectType):
    """
    Тип арендатора
    """

    class Meta:
        model = Tenant


class CommercialRentFormType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип формы на странице коммеции
    """

    class Meta:
        model = CommercialRentForm


class CommercialRentFormEmployeeType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип сотрудника на формы на странице коммерции
    """

    class Meta:
        model = CommercialRentFormEmployee


class CommercialPropertyPageType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип страницы коммерческой недвижимости
    """

    area_range = Field(RangeType)
    area_range_tenant = Field(RangeType)

    min_price = Int()
    min_rate_offers = Float()
    min_price_tenant = Int()

    tenant_block_title = String()

    class Meta:
        model = CommercialPropertyPage
        exclude = (
            "block_1_image_1",
            "block_1_image_2",
            "block_1_image_3",
            "block_1_image_4",
            "block_2_image_1",
            "block_2_image_2",
            "block_2_image_3",
            "block_2_image_4",
            "video_preview",
        )

    @staticmethod
    def resolve_area_range(obj, info, **kwargs):
        return {
            "min": getattr(obj, "min_area"),
            "max": getattr(obj, "max_area"),
        }

    @staticmethod
    def resolve_area_range_tenant(obj, info, **kwargs):
        return {
            "min": getattr(obj, "min_area_tenant"),
            "max": getattr(obj, "max_area_tenant"),
        }


class CommercialPropertyPageQuery(ObjectType):
    """
    Запросы страниц коммерческой недвижимости
    """

    all_tenants = List(TenantType, city=ID(required=True), description="Арендаторы")

    commercial_property_page = Field(
        CommercialPropertyPageType,
        city=ID(required=True),
        description="Фильтр по страницам коммерческой недвижимости",
    )
    commercial_property_page_specs = FacetFilterField(
        List(SpecType),
        filtered_type=CommercialPropertyPageType,
        filterset_class=CommercialPropertyPageFilterSet,
        method_name="specs",
        description="Спеки для страниц коммерческой недвижимости",
    )

    commercial_rent_forms = List(
        CommercialRentFormType, description="Формы на странице коммерческой недвижимости"
    )
    commercial_rent_forms_employee = List(
        CommercialRentFormEmployeeType,
        city_id=ID(),
        description="Сотрудники формы страницы коммерции",
    )

    @staticmethod
    def resolve_commercial_property_page(obj, info, city, **kwargs):
        try:
            _, city_id = from_global_id(city)
        except (UnicodeDecodeError, BinasciiError, ValueError):
            return None
        return query(
            CommercialPropertyPage.objects.filter(city=city_id)
            .annotate_area_range()
            .annotate_min_price()
            .annotate_min_rate_offers(),
            info,
        ).first()

    @staticmethod
    def resolve_all_tenants(obj, info, city, **kwargs):
        try:
            _, city_id = from_global_id(city)
        except (UnicodeDecodeError, BinasciiError, ValueError):
            return None
        return query(Tenant.objects.filter(cities=city_id).distinct(), info)

    @staticmethod
    def resolve_commercial_rent_forms(obj, info, **kwargs):
        return query(CommercialRentForm.objects.all(), info)

    @staticmethod
    def resolve_commercial_rent_forms_employee(obj, info, **kwargs):
        qs = CommercialRentFormEmployee.objects.all()
        if kwargs.get("city_id"):
            try:
                _, city_id = from_global_id(kwargs.get("city_id"))
                return query(qs.filter(city=city_id), info)
            except (UnicodeDecodeError, BinasciiError, ValueError):
                return None
        return query(qs, info)

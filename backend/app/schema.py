
from graphene_django.debug import DjangoDebug

import graphene
from auction.schema import AuctionMutation, AuctionQuery
from buildings.schema import BuildingQuery
from cities.schema import CityQuery
from commercial_project_page.schema import CommercialProjectPageQuery
from commercial_property_page.schema import CommercialPropertyPageQuery
from common.schema import (ChoiceFacetType, ChoiceSpecType, RangeFacetType,
                           RangeSpecType)
from company.schemas import (AboutQuery, DocumentQuery, PartnersQuery,
                             VacancyQuery)
from contacts.schema import OfficeQuery
from experiments.schema import ExperimentQuery
from favorite.schema import FavoriteMutation
from infras.schema import InfraQuery
from instagram.schema import InstagramQuery
from investments.schema import InvestmentsQuery
from landing.schema import LandingQuery
from landowners.schema import DevelopersLandownersQuery
from main_page.schema import MainPageQuery
from mortgage.schema import MortgageQuery
from news.schema import NewsQuery
from pop_ups.schema import PopUpQuery
from projects.schema import ProjectQuery, ProjectWebcamQuery
from properties.schema import PropertyMutation, PropertyQuery
from purchase.schema import PurchaseTypeQuery
from request_forms.schema import RequestMutation, RequestQuery
from users.schema import UserMutation
from vacancy.schemas import VacancyQuery as VC
from vk.schema import VkQuery


class Query(
    InstagramQuery,
    ProjectQuery,
    BuildingQuery,
    PropertyQuery,
    NewsQuery,
    OfficeQuery,
    DocumentQuery,
    CityQuery,
    PurchaseTypeQuery,
    MainPageQuery,
    InfraQuery,
    PartnersQuery,
    VacancyQuery,
    AboutQuery,
    CommercialPropertyPageQuery,
    MortgageQuery,
    RequestQuery,
    ProjectWebcamQuery,
    LandingQuery,
    AuctionQuery,
    CommercialProjectPageQuery,
    PopUpQuery,
    InvestmentsQuery,
    DevelopersLandownersQuery,
    VkQuery,
    ExperimentQuery,
    VC,
    graphene.ObjectType,
):
    node = graphene.relay.Node.Field()
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(
    RequestMutation,
    FavoriteMutation,
    AuctionMutation,
    PropertyMutation,
    UserMutation,
    graphene.ObjectType,
):
    node = graphene.relay.Node.Field()
    debug = graphene.Field(DjangoDebug, name="_debug")


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=(RangeSpecType, ChoiceSpecType, RangeFacetType, ChoiceFacetType),
)


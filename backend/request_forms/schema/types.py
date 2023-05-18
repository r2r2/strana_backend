from graphene_django import DjangoObjectType
from graphene_django_optimizer import OptimizedDjangoObjectType

from common.schema import MultiImageObjectTypeMeta
from graphene import ObjectType, String

from ..models import *

__all__ = [
    "LKDataType",
    "NewsRequestType",
    "CustomFormType",
    "MediaRequestType",
    "VacancyRequestType",
    "CustomFormEmployeeType",
    "SaleRequestType",
    "CustomRequestType",
    "CallbackRequestType",
    "ReservationRequestType",
    "ReservationLKRequestType",
    "ExcursionRequestType",
    "AgentRequestType",
    "OfficeRequestType",
    "TeaserRequestType",
    "LotCardRequestType",
    "AntiCorruptionRequestType",
    "ContractorRequestType",
    "PurchaseHelpRequestType",
    "CommercialRentRequestType",
    "NewsletterSubscriptionType",
    "DirectorCommunicateRequestType",
    "FlatListingRequestType",
    "FlatListingRequestFormType",
    "StartSaleRequestType",
    "PresentationRequestType",
    "MallTeamRequestType",
    "CommercialKotelnikiRequestType",
    "BeFirstRequestType",
    "AdvantageFormRequestType",
    "ShowRequestType",
]

from ..models import EKBStartSaleRequest, StartProjectsRequest


class LKDataType(ObjectType):
    """
    Данные для LK
    """

    name = String()
    image = String()
    image_plan = String()
    project = String()
    city = String()
    house = String()
    users_region = String()
    price = String()
    number = String()
    profitbase_id = String()
    floor = String()
    amo_pipeline_id = String()
    amo_responsible_user_id = String()
    booking_period = String()
    booking_price = String()
    address = String()
    token = String()


class VacancyRequestType(DjangoObjectType):
    """
    Тип отклика на вакансию
    """

    class Meta:
        model = VacancyRequest


class SaleRequestType(DjangoObjectType):
    """
    Тип заявки на продажу земельного участка
    """

    class Meta:
        model = SaleRequest


class CallbackRequestType(DjangoObjectType):
    """
    Тип заявки на обратную связь
    """

    class Meta:
        model = CallbackRequest


class ReservationRequestType(DjangoObjectType):
    """
    Тип заявки на бронирование
    """

    class Meta:
        model = ReservationRequest


class ReservationLKRequestType(DjangoObjectType):
    """
    Тип заявки на бронирование в ЛК
    """

    class Meta:
        model = ReservationLKRequest


class ExcursionRequestType(DjangoObjectType):
    """
    Тип записи на экскурсию
    """

    class Meta:
        model = ExcursionRequest


class MallTeamRequestType(DjangoObjectType):
    """
    Тип заявки с блока MallTeam
    """

    class Meta:
        model = MallTeamRequest


class AgentRequestType(DjangoObjectType):
    """
    Тип заявки агенств
    """

    class Meta:
        model = AgentRequest


class DirectorCommunicateRequestType(DjangoObjectType):
    """
    Тип запроса на связь с директором
    """

    class Meta:
        model = DirectorCommunicateRequest


class ContractorRequestType(DjangoObjectType):
    """
    Тип заявки для подрядчиков
    """

    class Meta:
        model = ContractorRequest


class NewsletterSubscriptionType(DjangoObjectType):
    """
    Тип подписки на рассылку
    """

    class Meta:
        model = NewsletterSubscription


class PurchaseHelpRequestType(DjangoObjectType):
    """
    Тип заявки на помощь с оформление покупки
    """

    class Meta:
        model = PurchaseHelpRequest


class CommercialRentRequestType(DjangoObjectType):
    """
    Тип заявки на аренду коммерческого помещения
    """

    class Meta:
        model = CommercialRentRequest


class MediaRequestType(DjangoObjectType):
    """
    Тип заявки для СМИ
    """

    class Meta:
        model = MediaRequest


class CustomFormType(DjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип кастомной формы
    """

    class Meta:
        model = CustomForm
        exclude = ("active",)


class CustomFormEmployeeType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип сотрудника на кастомой форме
    """

    class Meta:
        model = CustomFormEmployee


class CustomRequestType(DjangoObjectType):
    """
    Тип кастомной заявки
    """

    class Meta:
        model = CustomRequest


class TeaserRequestType(DjangoObjectType):
    """
    Тип заявки со слайда главной страницы
    """

    class Meta:
        model = TeaserRequest


class AntiCorruptionRequestType(DjangoObjectType):
    """
    Тип заявки о противодействии коррупции
    """

    class Meta:
        model = AntiCorruptionRequest


class NewsRequestType(DjangoObjectType):
    """
    Тип заявки со страницы новости
    """

    class Meta:
        model = NewsRequest


class OfficeRequestType(DjangoObjectType):
    """
    Тип заявки на встречу в офисе
    """

    class Meta:
        model = OfficeRequest


class LotCardRequestType(DjangoObjectType):
    """
    Тип заявки с карточки лота
    """

    class Meta:
        model = LotCardRequest


class FlatListingRequestType(DjangoObjectType):
    """
    Тип заявки в листинге квартир
    """

    class Meta:
        model = FlatListingRequest


class FlatListingRequestFormType(DjangoObjectType):
    """
    Тип формы заявки в листинге квартир
    """

    class Meta:
        model = FlatListingRequestForm


class StartSaleRequestType(DjangoObjectType):
    """
    Тип заявки на уведомление о старте продаж
    """

    class Meta:
        model = StartSaleRequest


class StartProjectsRequestType(DjangoObjectType):
    """
    Тип заявки на уведомление о старте продаж
    """

    class Meta:
        model = StartProjectsRequest


class EKBStartSaleRequestType(DjangoObjectType):
    """Тип заявки на уведомление о старте продаж в ЕКБ."""

    class Meta:
        model = EKBStartSaleRequest


class PresentationRequestType(DjangoObjectType):
    """
    Тип заявки на получения презентации
    """

    class Meta:
        model = PresentationRequest


class CommercialKotelnikiRequestType(DjangoObjectType):
    """
    Тип заявки коммерции Котельники
    """

    class Meta:
        model = CommercialKotelnikiRequest


class BeFirstRequestType(DjangoObjectType):
    """
    Тип заявки 'Узнать о старте продаж'
    """

    class Meta:
        model = BeFirstRequest


class AdvantageFormRequestType(DjangoObjectType):
    """
    Тип заявки с формы УТП
    """

    class Meta:
        model = AdvantageFormRequest


class ShowRequestType(DjangoObjectType):
    """Тип заявки записи на показ"""

    class Meta:
        model = ShowRequest

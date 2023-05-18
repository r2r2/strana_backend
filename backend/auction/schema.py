from graphene import Int, ObjectType, Mutation, Boolean, List, InputObjectType, String, Field
from graphene_django_optimizer import OptimizedDjangoObjectType

from common.schema import ErrorType
from common.utils import collect_form_errors
from .forms import NotificationForm
from .models import Auction, Notification, AuctionRules


class AuctionType(OptimizedDjangoObjectType):
    """Тип аукциона"""

    current_price = Int()

    is_current = Boolean()

    class Meta:
        model = Auction


class NotificationType(OptimizedDjangoObjectType):
    """Тип уведомления аукциона"""

    class Meta:
        model = Notification


class AuctionRulesType(OptimizedDjangoObjectType):
    """Тип правил аукциона"""

    class Meta:
        model = AuctionRules


class NotificationInput(InputObjectType):
    email = String(required=True)
    name = String(required=True)
    phone = String(required=True)
    lot_link = String(required=True)
    auction = Int(required=True)


class NotificationMutation(Mutation):
    """
    Мутация уведомления аукциона
    """

    ok = Boolean()
    errors = List(ErrorType)

    class Arguments:
        input = NotificationInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = NotificationForm(data=input)
        if form.is_valid():
            instance = form.save()
            instance.notify_manager()
            # instance.send_amocrm_lead(info.context)
            return cls(ok=True, errors=None)

        return cls(ok=False, errors=collect_form_errors(form))


class AuctionQuery(ObjectType):
    auction_rules = Field(AuctionRulesType, description="Правила аукциона")

    @staticmethod
    def resolve_auction_rules(obj, info, **kwargs):
        return AuctionRules.get_solo()


class AuctionMutation(ObjectType):

    auction_notification = NotificationMutation.Field(
        description="Мутация на создание уведомления аукциона"
    )

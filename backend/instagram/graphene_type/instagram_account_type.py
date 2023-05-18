from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from common.graphene import ExtendedConnection
from ..models import InstagramAccount


class InstagramAccountType(OptimizedDjangoObjectType):
    """
    Тип аккаунта инстаграмм
    """

    class Meta:
        model = InstagramAccount
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()

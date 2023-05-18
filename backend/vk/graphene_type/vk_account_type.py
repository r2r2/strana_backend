from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from common.graphene import ExtendedConnection
from ..models import VkAccount


class VkAccountType(OptimizedDjangoObjectType):
    """
    Тип аккаунта инстаграмм
    """

    class Meta:
        model = VkAccount
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()

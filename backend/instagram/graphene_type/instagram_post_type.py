from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from common.graphene import ExtendedConnection
from common.schema import MultiImageObjectTypeMeta
from ..filters import InstagramPostFilterSet
from ..models import InstagramPost


class InstagramPostType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип поста аккаунта инстаграмм
    """

    class Meta:
        model = InstagramPost
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()
        filterset_class = InstagramPostFilterSet

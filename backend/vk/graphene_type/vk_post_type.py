from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from common.graphene import ExtendedConnection
from common.schema import MultiImageObjectTypeMeta
from ..filters import VkPostFilterSet
from ..models import VkPost


class VkPostType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип поста аккаунта инстаграмм
    """

    class Meta:
        model = VkPost
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()
        filterset_class = VkPostFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(published=True)

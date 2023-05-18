from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from common.graphene import ExtendedConnection
from common.schema import MultiImageObjectTypeMeta
from ..models import VkPostImages


class VkPostImagesType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображения поста vk
    """

    class Meta:
        model = VkPostImages
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()

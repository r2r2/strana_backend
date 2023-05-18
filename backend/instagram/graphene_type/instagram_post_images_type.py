from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from common.graphene import ExtendedConnection
from common.schema import MultiImageObjectTypeMeta
from ..models import InstagramPostImages


class InstagramPostImagesType(OptimizedDjangoObjectType, metaclass=MultiImageObjectTypeMeta):
    """
    Тип изображения поста аккаунта инстаграмм
    """

    class Meta:
        model = InstagramPostImages
        connection_class = ExtendedConnection
        interfaces = (Node,)
        filter_fields = ()

from graphene import ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from ..graphene_type import VkPostType


class VkQuery(ObjectType):
    """
    Запросы инстаграмма
    """

    all_vk_post = DjangoFilterConnectionField(
        VkPostType, description="Список постов из vk",
    )

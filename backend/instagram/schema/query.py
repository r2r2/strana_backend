from graphene import ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from ..graphene_type import InstagramPostType


class InstagramQuery(ObjectType):
    """
    Запросы инстаграмма
    """

    all_instagram_post = DjangoFilterConnectionField(
        InstagramPostType, description="Список постов из инстаграмма",
    )

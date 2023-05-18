from graphene import String, Boolean, ObjectType, Mutation

from .models import SearchQuery


class CreateSearchQueryMutation(Mutation):
    """
    Создание поискового запроса
    """

    class Arguments:
        body = String(required=True)
        url = String(required=True)

    ok = Boolean()

    @classmethod
    def mutate(cls, obj, info, **kwargs):
        try:
            SearchQuery.objects.create(**kwargs)
        except:
            return cls(ok=False)
        return cls(ok=True)


class UserMutation(ObjectType):
    """
    Мутации пользователей
    """

    create_search_query = CreateSearchQueryMutation.Field(description="Создание поискового запроса")

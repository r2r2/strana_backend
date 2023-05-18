from graphene import ObjectType, String, Mutation, Boolean, Int
from graphql_relay import from_global_id


class CreateMutation(Mutation):
    """
    Добавление в избранное
    """

    class Arguments:
        id = String()

    count = Int()
    status = Boolean()

    def mutate(self, info, id):
        request = info.context
        _, pk = from_global_id(id)
        try:
            request.favorite.add(pk)
            status = True
        except ValueError:
            status = False
        count = request.favorite.count
        return CreateMutation(status=status, count=count)


class DeleteMutation(Mutation):
    """
    Удаление из избранного
    """

    class Arguments:
        id = String()

    count = Int()
    status = Boolean()

    def mutate(self, info, id):
        request = info.context
        _, pk = from_global_id(id)
        try:
            request.favorite.remove(pk)
            status = True
        except ValueError:
            status = False
        count = request.favorite.count
        return DeleteMutation(status=status, count=count)


class ClearMutation(Mutation):
    """
    Очистка избранных
    """

    count = Int()
    status = Boolean()

    def mutate(self, info):
        request = info.context
        request.favorite.clear()
        status = True
        count = request.favorite.count
        return ClearMutation(status=status, count=count)


class FavoriteMutation(ObjectType):
    """
    Запросы избранных
    """

    create_favorite = CreateMutation.Field()
    delete_favorite = DeleteMutation.Field()
    clear_favorite = ClearMutation.Field()

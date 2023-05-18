import factory

from ..models import User


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: "+7903{:07}".format(n))

    class Meta:
        model = User

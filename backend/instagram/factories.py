import factory
from projects.tests.factories import ProjectFactory
from .models import InstagramPost, InstagramAccount


class InstagramAccountFactory(factory.DjangoModelFactory):
    id = factory.Sequence(lambda n: 3241043700 + n)
    first = factory.Sequence(lambda n: 10 + n)
    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = InstagramAccount


class InstagramPostFactory(factory.DjangoModelFactory):
    id_instagram = factory.Sequence(lambda n: str(n))
    shortcode = factory.Sequence(lambda n: str(n))
    account = factory.SubFactory(InstagramAccountFactory)

    class Meta:
        model = InstagramPost

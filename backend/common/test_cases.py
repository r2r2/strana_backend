from django.contrib.sites.models import Site
from graphene_django.utils.testing import GraphQLTestCase

from app.schema import schema


class BaseTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql/"

    @classmethod
    def setUpClass(cls):
        Site.objects.get_current()
        return super().setUpClass()

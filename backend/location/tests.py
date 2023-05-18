from urllib.parse import urlencode
from django.http import QueryDict
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore

from .views import location


class LocationTestCase(TestCase):
    @staticmethod
    def _get_request() -> RequestFactory:
        request = RequestFactory()
        request.path = "/test"
        request.scheme = "https"
        request.COOKIES = {}
        request.session = SessionStore()
        request.GET = QueryDict("foo=bar")
        request.META = {"HTTP_X_REAL_IP": "127.0.0.1"}
        return request

    def test_location_save_query_params(self):

        request = self._get_request()
        response = location(request)

        self.assertIn(urlencode(request.GET), response.url)

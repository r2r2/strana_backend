from common.test_cases import BaseTestCase
from ..models import SearchQuery


class SearchQueryTestCase(BaseTestCase):
    def test_create_search_query(self):

        query = """
                mutation {
                    createSearchQuery(
                        body: "search body"
                        url: "https://google.com"
                    ) {
                        ok
                    }
                }
        """

        resp = self.query(query)
        resp_data = resp.json()

        self.assertResponseNoErrors(resp)
        self.assertEqual(1, SearchQuery.objects.count())
        self.assertTrue(resp_data["data"]["createSearchQuery"]["ok"])

from graphql_relay import to_global_id

from common.test_cases import BaseTestCase
from instagram.factories import InstagramPostFactory, InstagramAccountFactory
from projects.schema import ProjectType


class InstagramQueryTest(BaseTestCase):
    def setUp(self):
        self.projects = []
        for _ in range(5):
            account = InstagramAccountFactory()
            self.projects.append(account.project)
            for _ in range(5):
                InstagramPostFactory(account=account)

    def test_all_posts(self):
        query = """
                query {
                    allInstagramPost {
                        totalCount
                        edges {
                            node {
                                id
                                account {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_count = response_json["data"]["allInstagramPost"]["totalCount"]
        self.assertResponseNoErrors(response)
        self.assertEqual(response_count, 25)

        query = """
                query {
                    allInstagramPost (project: "%s") {
                        totalCount
                        edges {
                            node {
                                id
                                account {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        for project in self.projects:
            project_id = to_global_id(ProjectType.__name__, project.slug)
            response = self.query(query % project_id)
            response_json = response.json()
            response_count = response_json["data"]["allInstagramPost"]["totalCount"]
            self.assertResponseNoErrors(response)
            self.assertEqual(response_count, 5)

import json
from graphql_relay import to_global_id
from common.test_cases import BaseTestCase
from projects.tests.factories import ProjectFactory
from infras.tests.factories import (
    InfraCategoryFactory,
    InfraFactory,
    MainInfraFactory,
    SubInfraFactory,
    RoundInfraFactory,
)


class TestInfraCategoryQueries(BaseTestCase):
    def setUp(self) -> None:
        self.project_1 = ProjectFactory()
        self.project_1_id = to_global_id("ProjectType", self.project_1.slug)
        project_2 = ProjectFactory()
        category_1 = InfraCategoryFactory()
        self.category_1_id = to_global_id("InfraCategoryType", category_1.id)
        category_2 = InfraCategoryFactory()
        category_3 = InfraCategoryFactory()
        InfraFactory(project=self.project_1, category=category_1)
        InfraFactory(project=self.project_1, category=category_1)
        InfraFactory(project=self.project_1, category=category_2)
        InfraFactory(project=self.project_1, category=category_2)
        InfraFactory(project=self.project_1, category=category_2)
        InfraFactory(project=project_2, category=category_2)
        InfraFactory(project=project_2, category=category_3)

        [MainInfraFactory(project=self.project_1) for _ in range(5)]
        [MainInfraFactory(project=project_2) for _ in range(3)]
        [SubInfraFactory(project=self.project_1) for _ in range(6)]
        [SubInfraFactory(project=project_2) for _ in range(4)]
        [RoundInfraFactory(project=self.project_1) for _ in range(7)]
        [RoundInfraFactory(project=project_2) for _ in range(5)]

    def test_all_infra_category_query(self):
        query = """
                {
                allInfraCategories {
                    edges {
                        node {
                            id
                            name
                            icon
                        }
                    }
                }
            }
                """

        response = self.query(query)
        content = json.loads(response.content)
        infra_categories = content["data"]["allInfraCategories"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(infra_categories), 3)

    def test_infra_category_by_project(self):
        query = """
                 {
                    allInfraCategories(project: "%s") {
                        edges {
                            node {
                                name
                                infraSet {
                                    edges {
                                        node
                                        {
                                            name
                                            address
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(3):
            response = self.query(query % self.project_1_id)
            content = json.loads(response.content)
            infra_categories = content["data"]["allInfraCategories"]["edges"]

            self.assertResponseNoErrors(response)
            self.assertEqual(len(infra_categories), 2)

    def test_infra_with_params(self):
        query = """
                {
                    allInfra(project: "%s", category: "%s") {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(2):
            response = self.query(query % (self.project_1_id, self.category_1_id))
            content = json.loads(response.content)
            infra_categories = content["data"]["allInfra"]["edges"]

            self.assertResponseNoErrors(response)
            self.assertEqual(len(infra_categories), 2)

    def test_gen_infras(self):
        query = """
                query {
                    allMainInfra {
                        edges {
                            node {
                                name
                                maininfracontentSet {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_infras = response_json["data"]["allMainInfra"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_infras), 8)

        query = """
                query {
                    allSubInfra {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_infras = response_json["data"]["allSubInfra"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_infras), 10)

        query = """
                query {
                    allRoundInfra {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_infras = response_json["data"]["allRoundInfra"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_infras), 12)

    def test_gen_infras_filter(self):
        query = """
                query {
                    allMainInfra (project: "%s") {
                        edges {
                            node {
                                name
                                maininfracontentSet {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(query % self.project_1_id)
        response_json = response.json()
        response_infras = response_json["data"]["allMainInfra"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_infras), 5)

        query = """
                query {
                    allSubInfra (project: "%s")  {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query % self.project_1_id)
        response_json = response.json()
        response_infras = response_json["data"]["allSubInfra"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_infras), 6)

        query = """
                query {
                    allRoundInfra (project: "%s")  {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query % self.project_1_id)
        response_json = response.json()
        response_infras = response_json["data"]["allRoundInfra"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_infras), 7)

import json
from graphql_relay import to_global_id
from cities.schema import CityType
from cities.tests.factories import CityFactory
from common.test_cases import BaseTestCase
from purchase.tests.factory import (
    PurchaseTypeFactory,
    PurchaseTypeStepFactory,
    PurchaseTypeCategoryFactory,
)
from purchase.schema import PurchaseTypeGraphene


class AllPurchaseTypeTest(BaseTestCase):
    def test(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [PurchaseTypeCategoryFactory() for _ in range(6)]
        types = [PurchaseTypeFactory(city=cities[i % 2], category=categories[i]) for i in range(6)]

        query = """
                query {
                    allPurchaseTypes {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_purchase_types = content["data"]["allPurchaseTypes"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_purchase_types), 6)
        for i, res_type in enumerate(res_purchase_types):
            self.assertEqual(res_type["node"]["name"], types[i].name)

    def test_filter(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [PurchaseTypeCategoryFactory() for _ in range(6)]
        types = [PurchaseTypeFactory(city=cities[i % 2], category=categories[i]) for i in range(6)]

        query = """
                query {
                    allPurchaseTypes (city: "%s") {
                        edges {
                            node {
                                name
                                city {
                                    name
                                }
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(2):
            res = self.query(query % to_global_id(CityType.__name__, cities[0].id))
        content = json.loads(res.content)
        res_purchase_types = content["data"]["allPurchaseTypes"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_purchase_types), 3)
        for i, res_type in enumerate(res_purchase_types):
            self.assertEqual(res_type["node"]["name"], types[i * 2].name)
            self.assertEqual(res_type["node"]["city"]["name"], cities[0].name)

        query = """
                query {
                    allPurchaseTypes (category: "%s") {
                        edges {
                            node {
                                name
                                city {
                                    name
                                }
                                category {
                                    name
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query % categories[0].slug)
        content = json.loads(res.content)
        res_purchase_types = content["data"]["allPurchaseTypes"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_purchase_types), 1)
        self.assertEqual(res_purchase_types[0]["node"]["name"], types[0].name)
        self.assertEqual(res_purchase_types[0]["node"]["category"]["name"], categories[0].name)


class AllPurchaseTypeFacetsTest(BaseTestCase):
    def test(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [PurchaseTypeCategoryFactory() for _ in range(6)]
        [
            PurchaseTypeFactory(
                city=cities[i % 2], category=categories[i], is_commercial=i % 2 == 0
            )
            for i in range(6)
        ]

        query = """
                query {
                    allPurchaseTypesFacets {
                        count
                        facets {
                            name
                            ... on RangeFacetType {
                                range {
                                    min
                                    max
                                }
                            }
                            ... on ChoiceFacetType {
                                choices
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(4):
            res = self.query(query)
        content = json.loads(res.content)
        res_facets = content["data"]["allPurchaseTypesFacets"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_facets["count"], 6)
        self.assertEqual(len(res_facets["facets"]), 3)
        self.assertEqual(res_facets["facets"][0]["name"], "city")
        self.assertSetEqual(
            set(res_facets["facets"][0]["choices"]),
            {to_global_id(CityType.__name__, city.id) for city in cities},
        )
        self.assertEqual(res_facets["facets"][1]["name"], "category")
        self.assertSetEqual(
            set(res_facets["facets"][1]["choices"]),
            {category.slug for category in categories},
        )
        self.assertEqual(res_facets["facets"][2]["name"], "is_commercial")
        self.assertSetEqual(set(res_facets["facets"][2]["choices"]), {"true", "false"})


class AllPurchaseTypeSpecsTest(BaseTestCase):
    def test(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [PurchaseTypeCategoryFactory() for _ in range(6)]
        [PurchaseTypeFactory(city=cities[i % 2], category=categories[i]) for i in range(6)]

        query = """
                query {
                    allPurchaseTypesSpecs {
                        name
                        ... on RangeSpecType {
                            range {
                                min
                                max
                            }
                        }
                        ... on ChoiceSpecType {
                            choices {
                                value
                                label
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_specs = content["data"]["allPurchaseTypesSpecs"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_specs), 2)
        self.assertEqual(res_specs[0]["name"], "city")
        for i, choice in enumerate(res_specs[0]["choices"]):
            self.assertEqual(choice["value"], to_global_id(CityType.__name__, cities[i].id))
            self.assertEqual(choice["label"], cities[i].name)
        self.assertEqual(res_specs[1]["name"], "category")
        categories_slugs = [category.slug for category in categories]
        categories_names = [category.name for category in categories]
        for choice in res_specs[1]["choices"]:
            self.assertTrue(choice["value"] in categories_slugs)
            self.assertTrue(choice["label"] in categories_names)


class PurchaseTypeTest(BaseTestCase):
    def test(self):
        type_1 = PurchaseTypeFactory()
        steps_1 = [PurchaseTypeStepFactory(purchase_type=type_1) for _ in range(3)]
        type_2 = PurchaseTypeFactory()
        [PurchaseTypeStepFactory(purchase_type=type_2) for _ in range(3)]
        type_id = to_global_id(PurchaseTypeGraphene.__name__, type_1.id)

        query = """
                query {
                    purchaseType(id: "%s") {
                        name
                        purchasetypestepSet {
                            title
                        }
                        anotherPurchaseType {
                            name
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(query % type_id)
        content = json.loads(res.content)
        res_type = content["data"]["purchaseType"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_type["name"], type_1.name)
        self.assertEqual(len(res_type["purchasetypestepSet"]), 3)
        for i, res_step in enumerate(res_type["purchasetypestepSet"]):
            self.assertEqual(res_step["title"], steps_1[i].title)
        self.assertEqual(len(res_type["anotherPurchaseType"]), 1)
        self.assertEqual(res_type["anotherPurchaseType"][0]["name"], type_2.name)


class PurchaseTypeCategoryTest(BaseTestCase):
    def test(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [PurchaseTypeCategoryFactory() for _ in range(6)]
        [PurchaseTypeFactory(city=cities[i % 2], category=categories[i]) for i in range(6)]

        query = """
                query {
                    allPurchaseTypeCategories {
                        edges {
                            node {
                                name
                                order
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        response_json = response.json()
        response_categories = response_json["data"]["allPurchaseTypeCategories"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_categories), 6)

    def test_filter(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [PurchaseTypeCategoryFactory() for _ in range(6)]
        [PurchaseTypeFactory(city=cities[i % 2], category=categories[i]) for i in range(6)]

        query = """
                query {
                    allPurchaseTypeCategories(city: "%s") {
                        edges {
                            node {
                                name
                                order
                            }
                        }
                    }
                }
                """
        city_id = to_global_id(CityType.__name__, cities[0].id)

        with self.assertNumQueries(2):
            response = self.query(query % city_id)
        response_json = response.json()
        response_categories = response_json["data"]["allPurchaseTypeCategories"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_categories), 3)

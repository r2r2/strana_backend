import json
from graphql_relay import to_global_id
from common.test_cases import BaseTestCase
from cities.schema import CityType
from cities.tests.factories import CityFactory
from contacts.tests.factories import OfficeFactory, SubdivisionFactory, SocialFactory
from projects.schema import ProjectType
from projects.tests.factories import ProjectFactory


class AllOfficesTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(3)]
        offices = [OfficeFactory() for _ in range(3)]
        for office in offices:
            office.cities.add(*cities)
        not_active_city = CityFactory(active=False)
        not_active_city_office = OfficeFactory()
        not_active_city_office.cities.add(not_active_city)

        query = """
                query {
                    allOffices {
                        edges {
                            node {
                                name
                                cities {
                                    edges {
                                         node {
                                             name
                                         } 
                                    }
                                } 
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(query)
        content = json.loads(res.content)
        res_offices = content["data"]["allOffices"]["edges"]

        self.assertResponseNoErrors(res)
        for i, res_office in enumerate(res_offices):
            self.assertEqual(res_office["node"]["name"], offices[i].name)
            for j, city in enumerate(res_office["node"]["cities"]["edges"]):
                self.assertEqual(city["node"]["name"], cities[j].name)

    def test_with_subdivision(self):
        cities = [CityFactory() for _ in range(3)]
        offices = [OfficeFactory() for _ in range(3)]
        for office in offices:
            office.cities.add(*cities)
        subdivisions = [SubdivisionFactory(office=offices[i]) for i in range(3)]
        not_active_office = OfficeFactory(active=False)
        not_active_office.cities.add(cities[0])

        query = """
                query {
                    allOffices {
                        edges {
                            node {
                                name
                                cities {
                                    edges {
                                         node {
                                             name
                                         } 
                                    }
                                }
                                subdivisionSet {
                                    name
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(6):
            res = self.query(query)
        content = json.loads(res.content)
        res_offices = content["data"]["allOffices"]["edges"]

        self.assertResponseNoErrors(res)
        for i, res_office in enumerate(res_offices):
            self.assertEqual(res_office["node"]["name"], offices[i].name)
            for j, city in enumerate(res_office["node"]["cities"]["edges"]):
                self.assertEqual(city["node"]["name"], cities[j].name)
            self.assertEqual(len(res_office["node"]["subdivisionSet"]), 1)
            self.assertEqual(res_office["node"]["subdivisionSet"][0]["name"], subdivisions[i].name)

    def test_filter(self):
        cities = [CityFactory() for _ in range(3)]
        offices = [OfficeFactory() for _ in range(3)]
        for i, office in enumerate(offices):
            office.cities.add(cities[i])
        subdivisions = [SubdivisionFactory(office=offices[i]) for i in range(3)]
        city_id = to_global_id(CityType._meta.name, cities[0].id)

        query = """
                query {
                    allOffices (city: "%s") {
                        edges {
                            node {
                                name
                                cities {
                                    edges {
                                         node {
                                             id
                                         } 
                                    }
                                } 
                                subdivisionSet {
                                    name
                                }
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(4):
            res = self.query(query % city_id)
        content = json.loads(res.content)
        res_offices = content["data"]["allOffices"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_offices), 1)
        self.assertEqual(res_offices[0]["node"]["name"], offices[0].name)
        self.assertEqual(1, len(res_offices[0]["node"]["cities"]["edges"]))
        self.assertEqual(res_offices[0]["node"]["cities"]["edges"][0]["node"]["id"], city_id)
        self.assertEqual(len(res_offices[0]["node"]["subdivisionSet"]), 1)
        self.assertEqual(res_offices[0]["node"]["subdivisionSet"][0]["name"], subdivisions[0].name)

    def test_projects_filter(self):
        city = CityFactory()
        offices = [OfficeFactory() for _ in range(3)]
        for office in offices:
            office.cities.add(city)
        projects_1 = [ProjectFactory(city=city) for _ in range(3)]
        project_2 = ProjectFactory(city=city)
        projects_1_ids = list(map(lambda x: to_global_id(ProjectType.__name__, x.slug), projects_1))
        project_2_id = to_global_id(ProjectType.__name__, project_2.slug)
        for i in range(len(offices)):
            offices[i].projects.add(projects_1[i])
            offices[i].projects.add(project_2)

        query = """
                query {
                    allOffices (project: "%s") {
                        edges {
                            node {
                                name
                                cities {
                                    edges {
                                         node {
                                             id
                                         } 
                                    }
                                }
                                subdivisionSet {
                                    name
                                }
                            }
                        }
                    }
                }
                """

        for project_id in projects_1_ids:
            response = self.query(query % project_id)
            response_json = response.json()
            response_offices = response_json["data"]["allOffices"]["edges"]

            self.assertEqual(len(response_offices), 1)

        response = self.query(query % project_2_id)
        response_json = response.json()
        response_offices = response_json["data"]["allOffices"]["edges"]

        self.assertEqual(len(response_offices), 3)


class AllOfficesFacetsTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(3)]
        city_ids = [to_global_id(CityType._meta.name, city.id) for city in cities]
        offices = [OfficeFactory() for _ in range(3)]
        for i, office in enumerate(offices):
            office.cities.add(cities[i])
        not_active_city = CityFactory(active=False)
        not_active_office = OfficeFactory()
        not_active_office.cities.add(not_active_city)
        projects = [ProjectFactory(city=cities[i]) for i in range(3)]
        for i in range(len(offices)):
            offices[i].projects.add(projects[i])

        query = """
                query {
                    allOfficesFacets {
                        count
                        facets {
                            ...on RangeFacetType {
                                name
                                range {
                                    min
                                    max
                                }
                            }
                            ...on ChoiceFacetType {
                                name
                                choices
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(query)
        content = json.loads(res.content)
        res_facets = content["data"]["allOfficesFacets"]["facets"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_facets), 2)
        self.assertEqual(res_facets[0]["name"], "city")
        self.assertEqual(len(res_facets[0]["choices"]), 3)
        self.assertSetEqual(set(res_facets[0]["choices"]), set(city_ids))


class AllOfficesSpecsTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(3)]
        city_ids = [to_global_id(CityType._meta.name, city.id) for city in cities]
        offices = [OfficeFactory() for _ in range(3)]
        for i, office in enumerate(offices):
            office.cities.add(cities[i])
        not_active_city = CityFactory(active=False)
        not_active_office = OfficeFactory()
        not_active_office.cities.add(not_active_city)
        projects = [ProjectFactory(city=cities[i]) for i in range(3)]
        projects_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        for i in range(len(offices)):
            offices[i].projects.add(projects[i])

        query = """
                query {
                    allOfficesSpecs {
                        ...on RangeSpecType {
                            name
                            range {
                                min
                                max
                            }
                        }
                        ...on ChoiceSpecType {
                            name
                            choices {
                                label
                                value
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(1):
            res = self.query(query)
        content = json.loads(res.content)
        res_specs = content["data"]["allOfficesSpecs"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_specs), 1)
        self.assertEqual(res_specs[0]["name"], "city")
        self.assertEqual(len(res_specs[0]["choices"]), 3)
        for i, choice in enumerate(res_specs[0]["choices"]):
            self.assertEqual(choice["value"], city_ids[i])
            self.assertEqual(choice["label"], cities[i].name)


class AllSocialsTest(BaseTestCase):
    def test_default(self):
        [SocialFactory() for _ in range(5)]

        query = """
                query {
                    allSocials {
                        id
                        name
                        link
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_socials = response_json["data"]["allSocials"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_socials), 5)

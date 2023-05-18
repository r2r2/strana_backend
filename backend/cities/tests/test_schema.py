import json
from decimal import Decimal
from django.contrib.sites.models import Site
from graphql_relay import to_global_id
from cities.schema import CityType
from cities.tasks import calculate_city_fields_task
from cities.tests.factories import CityFactory, MapFactory
from commercial_property_page.tests.factories import CommercialPropertyPageFactory
from common.test_cases import BaseTestCase
from mortgage.constants import MortgageType
from mortgage.tests.factories import BankFactory, OfferFactory
from projects.tests.factories import ProjectFactory
from properties.tests.factories import FlatFactory, CommercialPremiseFactory, FlatRoomsMenuFactory


class AllCitiesTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(3)]
        CityFactory(active=False)
        calculate_city_fields_task()

        query = """
                query {
                    allCities {
                        edges {
                            node {
                                name
                                order
                                localCoords
                            }
                        }
                    }
                }
                """

        res = self.query(query)
        content = json.loads(res.content)
        res_cities = content["data"]["allCities"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_cities), len(cities))

        for i, city in enumerate(cities):
            res_city = res_cities[i]
            self.assertEqual(res_city["node"]["name"], city.name)
            self.assertEqual(res_city["node"]["order"], city.order)
            self.assertEqual(res_city["node"]["localCoords"], city.local_coords)

    def test_city(self):
        active_city = CityFactory()
        passive_city = CityFactory(active=False)
        active_city_id = to_global_id(CityType.__name__, active_city.id)
        passive_city_id = to_global_id(CityType.__name__, passive_city.id)
        calculate_city_fields_task()

        query = """
                query {
                    city (id: "%s") {
                        name
                        order
                    }
                }
                """

        response = self.query(query % active_city_id)
        response_json = response.json()
        response_city = response_json["data"]["city"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_city["name"], active_city.name)
        self.assertEqual(response_city["order"], active_city.order)

        response = self.query(query % passive_city_id)
        response_json = response.json()
        response_city = response_json["data"]["city"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_city, None)

    def test_current_city(self):
        site = Site.objects.get(domain="example.com")
        city = CityFactory(site=site)
        flat_rooms_menu = FlatRoomsMenuFactory(city=city)
        calculate_city_fields_task()

        query = """
                query {
                    currentCity {
                        id
                        name
                        localCoords
                        flatRoomsMenu {
                            rooms0Text
                            roomsZeroImagePreview
                            roomsZeroImageDisplay
                        }
                    }
                }
                """

        response = self.query(query)
        response_status = response.status_code
        response_json = response.json()
        response_city = response_json["data"]["currentCity"]

        AWAITABLE_STATUS = 200

        self.assertResponseNoErrors(response)
        self.assertEqual(response_status, AWAITABLE_STATUS)
        self.assertEqual(response_city["name"], city.name)
        self.assertEqual(response_city["localCoords"], city.local_coords)
        self.assertEqual(response_city["flatRoomsMenu"]["rooms0Text"], flat_rooms_menu.rooms_0_text)
        self.assertIsNotNone(response_city["flatRoomsMenu"]["roomsZeroImagePreview"])
        self.assertIsNotNone(response_city["flatRoomsMenu"]["roomsZeroImageDisplay"])

    def test_mortgages(self):
        site = Site.objects.get(domain="example.com")
        city = CityFactory(site=site)
        offers_1 = [
            OfferFactory(city=city, type=MortgageType.RESIDENTIAL) for _ in range(5)
        ]
        offers_2 = [
            OfferFactory(city=city, type=MortgageType.COMMERCIAL) for _ in range(5)
        ]
        calculate_city_fields_task()

        query = """
                query {
                    allCities {
                        edges {
                            node {
                                id
                                name
                                minMortgageCommercial
                                minMortgageResidential
                            }
                        }    
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_cities = response_json["data"]["allCities"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_cities), 1)
        self.assertEqual(response_cities[0]["node"]["minMortgageResidential"], offers_1[0].rate[0])
        self.assertEqual(response_cities[0]["node"]["minMortgageCommercial"], offers_2[0].rate[0])

    def test_min_prices(self):
        site = Site.objects.get(domain="example.com")
        city = CityFactory(site=site)
        projects = [ProjectFactory(city=city) for _ in range(5)]
        flats = [
            FlatFactory(project=projects[i], rooms=i, price=5000000 + 100000 * i, area=50 + i)
            for i in range(5)
        ]
        comms = [
            CommercialPremiseFactory(project=projects[i], price=5000000 + 100000 * i)
            for i in range(5)
        ]
        calculate_city_fields_task()
        query = """
                query {
                    allCities {
                        edges {
                            node {
                                id
                                name
                                minCommercialPrice
                                flats0MinPrice
                                flats1MinPrice
                                flats2MinPrice
                                flats3MinPrice
                                flats4MinPrice
                            }
                        }  
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_cities = response_json["data"]["allCities"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_cities), 1)
        self.assertEqual(
            int(Decimal(response_cities[0]["node"]["minCommercialPrice"])), comms[0].price
        )
        self.assertEqual(int(Decimal(response_cities[0]["node"]["flats0MinPrice"])), flats[0].price)
        self.assertEqual(int(Decimal(response_cities[0]["node"]["flats1MinPrice"])), flats[1].price)
        self.assertEqual(int(Decimal(response_cities[0]["node"]["flats2MinPrice"])), flats[2].price)
        self.assertEqual(int(Decimal(response_cities[0]["node"]["flats3MinPrice"])), flats[3].price)
        self.assertEqual(int(Decimal(response_cities[0]["node"]["flats4MinPrice"])), flats[4].price)

    def test_all_commercial_cities(self):
        site = Site.objects.get(domain="example.com")
        city = CityFactory(site=site)
        projects = [ProjectFactory(is_commercial=True, city=city) for _ in range(5)]
        comms = [
            CommercialPremiseFactory(
                project=projects[i], price=5000000 + 100000 * i, area=10 + i * 10
            )
            for i in range(5)
        ]
        calculate_city_fields_task()

        query = """
                query {
                    allCities(commercial: true) {
                        edges {
                            node {
                                id
                                name
                                minCommercialPrice
                                minCommercialArea
                                maxCommercialArea
                            }
                        }  
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_cities = response_json["data"]["allCities"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_cities), 0)

        CommercialPropertyPageFactory(city=city)

        response = self.query(query)
        response_json = response.json()
        response_cities = response_json["data"]["allCities"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_cities), 1)
        self.assertEqual(
            int(Decimal(response_cities[0]["node"]["minCommercialPrice"])), comms[0].price
        )
        self.assertEqual(
            int(Decimal(response_cities[0]["node"]["minCommercialArea"])), comms[0].area
        )
        self.assertEqual(
            int(Decimal(response_cities[0]["node"]["maxCommercialArea"])), comms[4].area
        )


class AllMapsTest(BaseTestCase):
    def test_all_maps(self):
        [MapFactory() for _ in range(10)]

        query = """
                query {
                    allMaps {
                        slug
                    }
                }
                """

        with self.assertNumQueries(1):
            response = self.query(query)

        response_json = response.json()
        response_maps = response_json["data"]["allMaps"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_maps), 10)

    def test_map(self):
        maps = [MapFactory() for _ in range(10)]

        query = """
                query {
                    map(slug: "%s") {
                        slug
                    }
                }
                """

        with self.assertNumQueries(1):
            response = self.query(query % maps[0].slug)

        response_json = response.json()
        response_map = response_json["data"]["map"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_map["slug"], maps[0].slug)

    def test_main_map(self):
        [MapFactory() for _ in range(10)]
        main_map = MapFactory(is_main=True)

        query = """
                query {
                    mainMap {
                        slug
                    }
                }
                """

        with self.assertNumQueries(1):
            response = self.query(query)

        response_json = response.json()
        response_map = response_json["data"]["mainMap"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_map["slug"], main_map.slug)

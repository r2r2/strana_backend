import json
from datetime import timedelta
from psycopg2.extras import NumericRange
from django.contrib.sites.models import Site
from django.utils.timezone import now
from graphql_relay import to_global_id
from graphene.utils.str_converters import to_camel_case
from cities.schema import CityType
from common.test_cases import BaseTestCase
from infras.tests.factories import MainInfraContentFactory, MainInfraFactory
from mortgage.constants import MortgageType
from mortgage.tests.factories import OfferFactory, BankFactory
from projects.schema import ProjectType
from cities.tests.factories import CityFactory
from projects.tests.factories import ProjectFactory
from buildings.tests.factories import BuildingFactory, SectionFactory, FloorFactory
from buildings.schema import BuildingType, FloorType
from properties.constants import PropertyStatus
from properties.schema import (
    FlatType,
    ParkingSpaceType,
    CommercialSpaceType,
    GlobalFlatType,
    GlobalParkingSpaceType,
    GlobalCommercialSpaceType,
    LayoutObjectType,
    FilteredFurnishType,
)
from properties.tests.factories import (
    FlatFactory,
    ParkingPlaceFactory,
    CommercialPremiseFactory,
    FurnishFactory,
    FurnishImageFactory,
    PropertyCardFactory,
    WindowViewFactory,
    WindowViewTypeFactory,
    WindowViewAngleFactory,
    MiniPlanPointFactory,
    MiniPlanPointAngleFactory,
    FeatureFactory,
    LayoutFactory,
    SpecialOfferFactory,
    PropertyPurposeFactory,
    CommercialApartmentFactory,
    FurnishPointFactory,
    ListingActionFactory,
)
from landing.tests.factories import LandingBlockFactory
from ..services import update_layouts
from ..models.config import PropertyConfig
from ..constants import FeatureType as FeatureTypeChoices, PropertyType


class FlatTest(BaseTestCase):
    def test_all_flats(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city_1)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        not_active_project = ProjectFactory(active=False)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        [ParkingPlaceFactory(project=project_1, building=building) for _ in range(3)]
        [CommercialPremiseFactory(project=project_1, building=building) for _ in range(3)]
        flats = [
            FlatFactory(project=project_1, building=building, section=section, floor=floor)
            for _ in range(3)
        ] + [FlatFactory(project=project_2)]
        FlatFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.BOOKED,
        )
        FlatFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.SOLD,
        )
        FlatFactory(project=not_active_project, building=building, section=section, floor=floor)
        FlatFactory(project=project_3, building=building, section=section, floor=floor)

        query = """
                {
                    allFlats {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allFlats"]["totalCount"], len(flats))
        self.assertEqual(len(response_flats), len(flats))
        for i, flat in enumerate(flats):
            flat_id = to_global_id(FlatType.__name__, flat.pk)
            self.assertEqual(response_flats[i]["node"]["id"], flat_id)
            self.assertEqual(response_flats[i]["node"]["number"], flat.number)

    def test_all_flats_with_params(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        building_id = to_global_id(BuildingType.__name__, buildings[0].id)
        [
            ParkingPlaceFactory(
                project=project,
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=0,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allFlats(building: "%s", rooms: ["0", "1"], priceMin: "%s", priceMax: "%s", 
                             areaMin: "%s", areaMax: "%s") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(
                query
                % (
                    building_id,
                    str(flats[0].price),
                    str(flats[5].price),
                    str(flats[0].area),
                    str(flats[5].area),
                )
            )
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[0].number)

    def test_all_flats_with_floor(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        section = SectionFactory(building=building)
        floors = [FloorFactory(section=section) for _ in range(10)]
        flats = [
            FlatFactory(project=project, building=building, section=section, floor=floors[i])
            for i in range(10)
        ]

        query = """
                {
                    allFlats(floorMin: "%s", floorMax: "%s") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query % (str(floors[4].number), str(floors[5].number)))
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[4].number)
        self.assertEqual(response_flats[1]["node"]["number"], flats[5].number)

    def test_all_flats_with_project(self):
        projects = [ProjectFactory() for _ in range(2)]
        flats = [FlatFactory(project=projects[i % 2]) for i in range(6)]

        query = """
                {
                    allFlats(project: "%s") {
                        edges {
                            node {
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query % to_global_id(ProjectType.__name__, projects[0].slug))
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 3)
        for i in range(3):
            self.assertEqual(response_flats[i]["node"]["number"], flats[i * 2].number)

    def test_all_flats_with_building(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(6)]
        flats = [FlatFactory(project=project, building=buildings[i]) for i in range(6)]

        query = """
                {
                    allFlats(building: ["%s", "%s"]) {
                        edges {
                            node {
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(
                query
                % (
                    to_global_id(BuildingType.__name__, buildings[0].id),
                    to_global_id(BuildingType.__name__, buildings[4].id),
                )
            )
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[0].number)
        self.assertEqual(response_flats[1]["node"]["number"], flats[4].number)

    def test_all_flats_with_order(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        building_id = to_global_id(BuildingType.__name__, buildings[0].id)
        [
            ParkingPlaceFactory(
                project=project,
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=0,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allFlats(building: "%s", rooms: ["0", "1"], priceMin: "%s", priceMax: "%s", 
                             areaMin: "%s", areaMax: "%s", orderBy: "-price") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(
                query
                % (
                    building_id,
                    str(flats[0].price),
                    str(flats[5].price),
                    str(flats[0].area),
                    str(flats[5].area),
                )
            )
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[4].number)
        self.assertEqual(response_flats[1]["node"]["number"], flats[0].number)

    def test_all_flats_with_ids(self):
        project = ProjectFactory()
        flats = [FlatFactory(project=project) for _ in range(9)]
        flats_ids = [to_global_id(FlatType.__name__, flat.pk) for flat in flats]

        query = """
                {
                    allFlats(id: ["%s", "%s", "%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query % (flats_ids[0], flats_ids[4], flats_ids[8]))
        content = json.loads(response.content)
        response_flats = content["data"]["allFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 3)
        self.assertEqual(response_flats[0]["node"]["id"], flats_ids[0])
        self.assertEqual(response_flats[1]["node"]["id"], flats_ids[4])
        self.assertEqual(response_flats[2]["node"]["id"], flats_ids[8])

    def test_all_flats_specs(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        building_ids = [to_global_id(BuildingType.__name__, building.id) for building in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 5
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allFlatsSpecs {
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
        with self.assertNumQueries(9):
            response = self.query(query)
        content = json.loads(response.content)
        response_specs = content["data"]["allFlatsSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 15)
        self.assertEqual(response_specs[0]["name"], "building")
        for i in range(len(buildings)):
            self.assertEqual(response_specs[0]["choices"][i]["label"], buildings[i].name_display)
            self.assertEqual(response_specs[0]["choices"][i]["value"], building_ids[i])
        self.assertEqual(response_specs[1]["name"], "project")
        for i in range(len(projects)):
            self.assertEqual(response_specs[1]["choices"][i]["label"], projects[i].name)
            self.assertEqual(response_specs[1]["choices"][i]["value"], project_ids[i])
        self.assertEqual(response_specs[2]["name"], "price")
        self.assertEqual(response_specs[2]["range"]["min"], flats[0].price)
        self.assertEqual(response_specs[2]["range"]["max"], flats[-1].price)
        self.assertEqual(response_specs[3]["name"], "area")
        self.assertEqual(response_specs[3]["range"]["min"], flats[0].area)
        self.assertEqual(response_specs[3]["range"]["max"], flats[-1].area)
        self.assertEqual(response_specs[4]["name"], "completion_date")
        for i in range(len(buildings)):
            self.assertEqual(
                response_specs[4]["choices"][i]["label"],
                f"{buildings[i].ready_quarter} кв. {buildings[i].built_year}",
            )
            self.assertEqual(
                response_specs[4]["choices"][i]["value"],
                f"{buildings[i].built_year}-{buildings[i].ready_quarter}",
            )
        self.assertEqual(response_specs[6]["name"], "features")
        self.assertEqual(response_specs[7]["name"], "special_offers")
        self.assertEqual(response_specs[8]["name"], "rooms")
        self.assertEqual(
            response_specs[8]["choices"],
            [
                {"label": "Студия", "value": "0"},
                {"label": "1", "value": "1"},
                {"label": "2", "value": "2"},
                {"label": "3", "value": "3"},
                {"label": "4+", "value": "4"},
            ],
        )
        self.assertEqual(response_specs[9]["name"], "floor")
        self.assertEqual(response_specs[9]["range"]["min"], floors[0].number)
        self.assertEqual(response_specs[9]["range"]["max"], floors[-1].number)

    def test_all_flats_facets(self):
        current_date = now().date()
        dates = [current_date - timedelta(days=93), current_date + timedelta(days=93)]
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [
            BuildingFactory(
                project=projects[i % 3],
                built_year=dates[i].year,
                ready_quarter=(dates[i].month - 1 // 3) + 1,
            )
            for i in range(2)
        ]
        building_ids = [to_global_id(BuildingType.__name__, building.id) for building in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 5
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                facing=(i % 2 == 0),
                has_view=(i % 2 == 0),
                has_terrace=(i % 2 == 0),
                has_parking=(i % 2 == 0),
                is_duplex=(i % 2 == 0),
                has_high_ceiling=(i % 2 == 0),
                has_panoramic_windows=(i % 2 == 0),
                has_two_sides_windows=(i % 2 == 0),
                balconies_count=i % 3,
                loggias_count=i % 3,
                stores_count=i % 3,
                wardrobes_count=i % 3,
                installment=(i % 2 == 0),
                favorable_rate=(i % 2 == 0),
                preferential_mortgage=(i % 2 == 0),
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]

        query = """
                {
                    allFlatsFacets {
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

        with self.assertNumQueries(22):
            response = self.query(query)
        content = json.loads(response.content)
        response_facets = content["data"]["allFlatsFacets"]["facets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_facets), 18)
        for facet in response_facets:
            if facet["name"] == "building":
                self.assertSetEqual(set(facet["choices"]), set(building_ids))
            elif facet["name"] == "project":
                for i in range(len(projects)):
                    self.assertEqual(facet["choices"][i], project_ids[i])
            elif facet["name"] == "price":
                self.assertEqual(facet["range"]["min"], flats[0].price)
                self.assertEqual(facet["range"]["max"], flats[-1].price)
            elif facet["name"] == "area":
                self.assertEqual(facet["range"]["min"], flats[0].area)
                self.assertEqual(facet["range"]["max"], flats[-1].area)
            elif facet["name"] == "completion_date":
                self.assertEqual(
                    facet["choices"],
                    [f"{building.built_year}-{building.ready_quarter}" for building in buildings],
                )
            elif facet["name"] == "action":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "rooms":
                rooms_set = {str(i) if i <= 4 else "4" for i in range(min_rooms, max_rooms + 1)}
                self.assertSetEqual(set(facet["choices"]), rooms_set)
            elif facet["name"] == "floor":
                self.assertEqual(facet["range"]["min"], floors[0].number)
                self.assertEqual(facet["range"]["max"], floors[-1].number)
            elif facet["name"] == "balconiesCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "loggiasCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "storesCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "wardrobesCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "is_favorite":
                self.assertSetEqual(set(facet["choices"]), {"false"})

    def test_flat(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=1 + i % 2,
                price=5000000 + 100000 * i,
            )
            for i in range(12)
        ]
        flat_id = to_global_id(FlatType.__name__, flats[0].id)

        query = """
                {
                    flat(id: "%s") {
                        id
                    }
                }
                """

        with self.assertNumQueries(1):
            res = self.query(query % flat_id)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["flat"]["id"], flat_id)

    def test_all_furnishes(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        flat_1 = FlatFactory(project=project, building=building)
        flat_2 = FlatFactory(project=project, building=building)
        furnishes = [
            FurnishFactory(order=3),
            FurnishFactory(order=1),
            FurnishFactory(order=2),
            FurnishFactory(order=2),
            FurnishFactory(order=1),
            FurnishFactory(order=2),
        ]
        flat_1.furnish_set.add(furnishes[0])
        flat_1.furnish_set.add(furnishes[1])
        flat_1.furnish_set.add(furnishes[2])
        flat_2.furnish_set.add(furnishes[3])
        flat_2.furnish_set.add(furnishes[4])

        query = """
                {
                    allFlats {
                        edges {
                            node {
                                furnishSet {
                                    id
                                    name
                                    description
                                    order
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(query)
        content = json.loads(res.content)
        response_flats = content["data"]["allFlats"]["edges"]
        furnish_set_1 = response_flats[0]["node"]["furnishSet"]
        furnish_set_2 = response_flats[1]["node"]["furnishSet"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(len(furnish_set_1), 3)
        self.assertEqual(furnish_set_1[0]["id"], str(furnishes[1].id))
        self.assertEqual(furnish_set_1[1]["id"], str(furnishes[2].id))
        self.assertEqual(furnish_set_1[2]["id"], str(furnishes[0].id))
        self.assertEqual(len(furnish_set_2), 2)
        self.assertEqual(furnish_set_2[0]["id"], str(furnishes[4].id))
        self.assertEqual(furnish_set_2[1]["id"], str(furnishes[3].id))
        for furnish in furnish_set_1 + furnish_set_2:
            self.assertListEqual(list(furnish.keys()), ["id", "name", "description", "order"])

    def test_furnish_images(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        flat = FlatFactory(project=project, building=building)
        flat_id = to_global_id(FlatType.__name__, flat.id)
        furnishes = [FurnishFactory() for _ in range(2)]
        for furnish in furnishes:
            flat.furnish_set.add(furnish)
        images = [FurnishImageFactory(furnish=furnishes[i % 2], order=10 - i) for i in range(10)]

        query = """
                {
                    flat(id: "%s") {
                        furnishSet {
                            id
                            imageSet {
                                id
                                order
                                file
                                fileDisplay
                                filePreview
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(query % flat_id)
        content = json.loads(res.content)
        response_furnishes = content["data"]["flat"]["furnishSet"]
        image_set = response_furnishes[0]["imageSet"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(response_furnishes), 2)
        self.assertEqual(len(image_set), 5)
        self.assertEqual(image_set[0]["id"], str(images[8].id))
        self.assertEqual(image_set[1]["id"], str(images[6].id))
        self.assertEqual(image_set[2]["id"], str(images[4].id))
        self.assertEqual(image_set[3]["id"], str(images[2].id))
        self.assertEqual(image_set[4]["id"], str(images[0].id))
        for image in image_set:
            self.assertListEqual(
                list(image.keys()), ["id", "order", "file", "fileDisplay", "filePreview"]
            )


class ParkingSpaceTest(BaseTestCase):
    def test_all_parking_spaces(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city_1)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        not_active_project = ProjectFactory(active=False)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        parking_spaces = [
            ParkingPlaceFactory(project=project_1, building=building, section=section, floor=floor)
            for _ in range(3)
        ] + [ParkingPlaceFactory(project=project_2)]
        ParkingPlaceFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.SOLD,
        )
        ParkingPlaceFactory(
            project=not_active_project, building=building, section=section, floor=floor
        )
        ParkingPlaceFactory(project=project_3, building=building, section=section, floor=floor)

        query = """
                {
                    allParkingSpaces {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        content = json.loads(response.content)
        res_parking_spaces = content["data"]["allParkingSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allParkingSpaces"]["totalCount"], len(parking_spaces))
        self.assertEqual(len(res_parking_spaces), len(parking_spaces))
        for i, parking_space in enumerate(parking_spaces):
            parking_space_id = to_global_id(ParkingSpaceType.__name__, parking_space.pk)
            self.assertEqual(res_parking_spaces[i]["node"]["id"], parking_space_id)
            self.assertEqual(res_parking_spaces[i]["node"]["number"], parking_space.number)

    def test_all_parking_spaces_with_params(self):
        projects = [ProjectFactory() for _ in range(2)]
        buildings = [BuildingFactory(project=projects[i]) for i in range(2)]
        sections = [SectionFactory(building=buildings[i]) for i in range(2)]
        floors = [FloorFactory(section=sections[i]) for i in range(2)]
        parking_spaces = [
            ParkingPlaceFactory(
                project=projects[i % 2],
                building=buildings[i % 2],
                section=sections[i % 2],
                floor=floors[i % 2],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(8)
        ]
        project_id = to_global_id(ProjectType.__name__, projects[0].slug)

        query = """
                {
                    allParkingSpaces (
                        project: "%s", priceMin: "%s", priceMax: "%s",
                        areaMin: "%s", areaMax: "%s", completionDate: "%s", action: false
                    ) {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(
                query
                % (
                    project_id,
                    str(parking_spaces[0].price),
                    str(parking_spaces[3].price),
                    str(parking_spaces[0].area),
                    str(parking_spaces[1].area),
                    f"{buildings[0].built_year}-{buildings[0].ready_quarter}",
                )
            )
        content = json.loads(response.content)
        res_parking_spaces = content["data"]["allParkingSpaces"]["edges"]
        parking_space_id = to_global_id(ParkingSpaceType.__name__, parking_spaces[0].pk)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allParkingSpaces"]["totalCount"], 1)
        self.assertEqual(len(res_parking_spaces), 1)
        self.assertEqual(res_parking_spaces[0]["node"]["id"], parking_space_id)
        self.assertEqual(res_parking_spaces[0]["node"]["number"], parking_spaces[0].number)

    def test_all_parking_spaces_specs(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        building_ids = [to_global_id(BuildingType.__name__, b.id) for b in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 3
        parking_spaces = [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allParkingSpacesSpecs {
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

        with self.assertNumQueries(7):
            response = self.query(query)
        content = json.loads(response.content)
        response_specs = content["data"]["allParkingSpacesSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 8)
        self.assertEqual(response_specs[0]["name"], "project")
        for i in range(len(projects)):
            self.assertEqual(response_specs[0]["choices"][i]["label"], projects[i].name)
            self.assertEqual(response_specs[0]["choices"][i]["value"], project_ids[i])
        self.assertEqual(response_specs[1]["name"], "building")
        for i in range(len(buildings)):
            self.assertEqual(response_specs[1]["choices"][i]["label"], buildings[i].name_display)
            self.assertEqual(response_specs[1]["choices"][i]["value"], building_ids[i])
        self.assertEqual(response_specs[2]["name"], "price")
        self.assertEqual(response_specs[2]["range"]["min"], parking_spaces[0].price)
        self.assertEqual(response_specs[2]["range"]["max"], parking_spaces[-1].price)
        self.assertEqual(response_specs[3]["name"], "area")
        self.assertEqual(response_specs[3]["range"]["min"], parking_spaces[0].area)
        self.assertEqual(response_specs[3]["range"]["max"], parking_spaces[-1].area)
        self.assertEqual(response_specs[4]["name"], "completion_date")
        for i in range(len(buildings)):
            self.assertEqual(
                response_specs[4]["choices"][i]["label"],
                f"{buildings[i].ready_quarter} кв. {buildings[i].built_year}",
            )
            self.assertEqual(
                response_specs[4]["choices"][i]["value"],
                f"{buildings[i].built_year}-{buildings[i].ready_quarter}",
            )

    def test_all_parking_spaces_facets(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        building_ids = [to_global_id(BuildingType.__name__, b.id) for b in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 3
        parking_spaces = [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                facing=(i % 2 == 0),
                has_view=(i % 2 == 0),
                has_terrace=(i % 2 == 0),
                has_parking=(i % 2 == 0),
                is_duplex=(i % 2 == 0),
                has_high_ceiling=(i % 2 == 0),
                has_panoramic_windows=(i % 2 == 0),
                has_two_sides_windows=(i % 2 == 0),
                balconies_count=i % 3,
                loggias_count=i % 3,
                stores_count=i % 3,
                wardrobes_count=i % 3,
                installment=(i % 2 == 0),
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]

        query = """
                {
                    allParkingSpacesFacets {
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
        with self.assertNumQueries(11):
            response = self.query(query)
        content = json.loads(response.content)
        response_facets = content["data"]["allParkingSpacesFacets"]["facets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_facets), 10)
        for facet in response_facets:
            if facet["name"] == "project":
                for i in range(len(projects)):
                    self.assertEqual(facet["choices"][i], project_ids[i])
            elif facet["name"] == "building":
                for i in range(len(buildings)):
                    self.assertEqual(facet["choices"][i], building_ids[i])
            elif facet["name"] == "price":
                self.assertEqual(facet["range"]["min"], parking_spaces[0].price)
                self.assertEqual(facet["range"]["max"], parking_spaces[-1].price)
            elif facet["name"] == "area":
                self.assertEqual(facet["range"]["min"], parking_spaces[0].area)
                self.assertEqual(facet["range"]["max"], parking_spaces[-1].area)
            elif facet["name"] == "completion_date":
                self.assertEqual(
                    facet["choices"],
                    [f"{building.built_year}-{building.ready_quarter}" for building in buildings],
                )
            elif facet["name"] == "action":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})


class CommercialSpaceTest(BaseTestCase):
    def test_all_commercial_spaces(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city_1)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        not_active_project = ProjectFactory(active=False)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        commercial_spaces = [
            CommercialPremiseFactory(
                project=project_1, building=building, section=section, floor=floor
            )
            for _ in range(3)
        ] + [CommercialPremiseFactory(project=project_2)]
        CommercialPremiseFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.BOOKED,
        )
        CommercialPremiseFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.SOLD,
        )
        CommercialPremiseFactory(
            project=not_active_project, building=building, section=section, floor=floor
        )
        CommercialPremiseFactory(project=project_3, building=building, section=section, floor=floor)

        query = """
                {
                    allCommercialSpaces {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        content = json.loads(response.content)
        res_commercial_spaces = content["data"]["allCommercialSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["allCommercialSpaces"]["totalCount"], len(commercial_spaces)
        )
        self.assertEqual(len(res_commercial_spaces), len(commercial_spaces))
        for i, commercial_space in enumerate(commercial_spaces):
            commercial_space_id = to_global_id(CommercialSpaceType.__name__, commercial_space.pk)
            self.assertEqual(res_commercial_spaces[i]["node"]["id"], commercial_space_id)
            self.assertEqual(res_commercial_spaces[i]["node"]["number"], commercial_space.number)

    def test_all_commercial_spaces_with_params(self):
        projects = [ProjectFactory() for _ in range(2)]
        buildings = [BuildingFactory(project=projects[i]) for i in range(2)]
        sections = [SectionFactory(building=buildings[i]) for i in range(2)]
        floors = [FloorFactory(section=sections[i]) for i in range(2)]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects[i % 2],
                building=buildings[i % 2],
                section=sections[i % 2],
                floor=floors[i % 2],
                price=5000000 + 100000 * i,
                area=50 + i,
                has_tenant=(i % 2 == 0),
            )
            for i in range(8)
        ]

        project_id = to_global_id(ProjectType.__name__, projects[0].slug)

        query = """
                {
                    allCommercialSpaces (
                        project: "%s", priceMin: "%s", priceMax: "%s",
                        areaMin: "%s", areaMax: "%s", completionDate: "%s",
                        action: false, hasTenant: true
                    ) {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(
                query
                % (
                    project_id,
                    str(commercial_spaces[0].price),
                    str(commercial_spaces[3].price),
                    str(commercial_spaces[0].area),
                    str(commercial_spaces[1].area),
                    f"{buildings[0].built_year}-{buildings[0].ready_quarter}",
                )
            )
        content = json.loads(response.content)
        res_commercial_spaces = content["data"]["allCommercialSpaces"]["edges"]
        commercial_space_id = to_global_id(CommercialSpaceType.__name__, commercial_spaces[0].pk)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allCommercialSpaces"]["totalCount"], 1)
        self.assertEqual(len(res_commercial_spaces), 1)
        self.assertEqual(res_commercial_spaces[0]["node"]["id"], commercial_space_id)
        self.assertEqual(res_commercial_spaces[0]["node"]["number"], commercial_spaces[0].number)

    def test_all_commercial_spaces_completed(self):
        current_date = now().date()
        future_date = current_date + timedelta(days=93)
        past_date = current_date - timedelta(days=93)
        project = ProjectFactory()
        buildings = [
            BuildingFactory(
                project=project, built_year=date.year, ready_quarter=(date.month - 1 // 3) + 1
            )
            for date in [past_date, future_date]
        ]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allCommercialSpaces(completed: true) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        content = json.loads(response.content)
        response_commercial_spaces = content["data"]["allCommercialSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_commercial_spaces), 6)
        for i, flat in enumerate(response_commercial_spaces):
            self.assertEqual(
                response_commercial_spaces[i]["node"]["number"], commercial_spaces[i * 2].number
            )

    def test_all_commercial_spaces_specs(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        building_ids = [to_global_id(BuildingType.__name__, b.id) for b in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 3
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allCommercialSpacesSpecs {
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

        with self.assertNumQueries(7):
            response = self.query(query)
        content = json.loads(response.content)
        response_specs = content["data"]["allCommercialSpacesSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 8)
        self.assertEqual(response_specs[0]["name"], "project")
        for i in range(len(projects)):
            self.assertEqual(response_specs[0]["choices"][i]["label"], projects[i].name)
            self.assertEqual(response_specs[0]["choices"][i]["value"], project_ids[i])
        self.assertEqual(response_specs[1]["name"], "building")
        for i in range(len(buildings)):
            self.assertEqual(response_specs[1]["choices"][i]["label"], buildings[i].name_display)
            self.assertEqual(response_specs[1]["choices"][i]["value"], building_ids[i])
        self.assertEqual(response_specs[2]["name"], "price")
        self.assertEqual(response_specs[2]["range"]["min"], commercial_spaces[0].price)
        self.assertEqual(response_specs[2]["range"]["max"], commercial_spaces[-1].price)
        self.assertEqual(response_specs[3]["name"], "area")
        self.assertEqual(response_specs[3]["range"]["min"], commercial_spaces[0].area)
        self.assertEqual(response_specs[3]["range"]["max"], commercial_spaces[-1].area)
        self.assertEqual(response_specs[4]["name"], "completion_date")
        for i in range(len(buildings)):
            self.assertEqual(
                response_specs[4]["choices"][i]["label"],
                f"{buildings[i].ready_quarter} кв. {buildings[i].built_year}",
            )
            self.assertEqual(
                response_specs[4]["choices"][i]["value"],
                f"{buildings[i].built_year}-{buildings[i].ready_quarter}",
            )

    def test_all_commercial_spaces_facets(self):
        current_date = now().date()
        dates = [current_date - timedelta(days=93), current_date + timedelta(days=93)]
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [
            BuildingFactory(
                project=projects[i % 3],
                built_year=dates[i].year,
                ready_quarter=(dates[i].month - 1 // 3) + 1,
            )
            for i in range(2)
        ]
        building_ids = [to_global_id(BuildingType.__name__, b.id) for b in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 3
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=50 + i,
                promo_start=now() - timedelta(days=5 - i),
                has_tenant=(i % 2 == 0),
                installment=(i % 2 == 0),
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                facing=(i % 2 == 0),
                has_view=(i % 2 == 0),
                has_terrace=(i % 2 == 0),
                has_parking=(i % 2 == 0),
                is_duplex=(i % 2 == 0),
                has_high_ceiling=(i % 2 == 0),
                has_panoramic_windows=(i % 2 == 0),
                has_two_sides_windows=(i % 2 == 0),
                balconies_count=i % 3,
                loggias_count=i % 3,
                stores_count=i % 3,
                wardrobes_count=i % 3,
                installment=(i % 2 == 0),
            )
            for i in range(12)
        ]

        query = """
                {
                    allCommercialSpacesFacets {
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

        with self.assertNumQueries(13):
            response = self.query(query)
        content = json.loads(response.content)
        response_facets = content["data"]["allCommercialSpacesFacets"]["facets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_facets), 12)
        for facet in response_facets:
            if facet["name"] == "project":
                for i in range(len(projects)):
                    self.assertEqual(facet["choices"][i], project_ids[i])
            elif facet["name"] == "building":
                for i in range(len(buildings)):
                    self.assertEqual(facet["choices"][i], building_ids[i])
            elif facet["name"] == "price":
                self.assertEqual(facet["range"]["min"], commercial_spaces[0].price)
                self.assertEqual(facet["range"]["max"], commercial_spaces[-1].price)
            elif facet["name"] == "area":
                self.assertEqual(facet["range"]["min"], commercial_spaces[0].area)
                self.assertEqual(facet["range"]["max"], commercial_spaces[-1].area)
            elif facet["name"] == "completion_date":
                self.assertEqual(
                    facet["choices"],
                    [f"{building.built_year}-{building.ready_quarter}" for building in buildings],
                )
            elif facet["name"] == "action":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "hasTenant":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "completed":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "is_favorite":
                self.assertSetEqual(set(facet["choices"]), {"false"})

    def test_commercial_space(self):
        project = ProjectFactory()
        commercial_spaces = [
            CommercialPremiseFactory(project=project, price=5000000 + 500000 * i, area=50 + 10 * i)
            for i in range(5)
        ]
        commercial_space_ids = [
            to_global_id(CommercialSpaceType.__name__, n.id) for n in commercial_spaces
        ]

        query = """
                {
                    commercialSpace (id: "%s") {
                        id
                    }
                }
                """

        with self.assertNumQueries(1):
            response = self.query(query % commercial_space_ids[2])
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["commercialSpace"]["id"], commercial_space_ids[2])


class UniquePlanTest(BaseTestCase):
    def test_all_unique_plans(self):
        projects = list()
        for i in range(5):
            project = ProjectFactory()
            projects.append(project)
            [
                FlatFactory(
                    project=project,
                    rooms=i + 1,
                    plan_code=f"{i}_flat#{j + 1}",
                    price=1000000 * (j + 1),
                )
                for j in range(5)
            ]
        project_ids = list(map(lambda x: to_global_id(ProjectType.__name__, x.slug), projects))

        query = """
                query {
                    allUniquePlans {
                        edges{
                            node {
                                id
                                plan
                                planCode
                                type
                                rooms
                                project {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_plans = response_json["data"]["allUniquePlans"]["edges"]
        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_plans), 25)

        query = """
                 query {
                    allUniquePlans (rooms: ["%s"]) {
                        edges{
                            node {
                                id
                                plan
                                planCode
                                type
                                project {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        for i in range(5):
            response = self.query(query % str(i + 1 if (i + 1) <= 4 else 4))
            response_json = response.json()
            response_plans = response_json["data"]["allUniquePlans"]["edges"]
            self.assertResponseNoErrors(response)
            self.assertTrue(len(response_plans) in (5, 10))

        query = """
                query {
                    allUniquePlans (project: "%s") {
                        edges{
                            node {
                                id
                                plan
                                planCode
                                type
                                project {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        for project_id in project_ids:
            response = self.query(query % project_id)
            response_json = response.json()
            response_plans = response_json["data"]["allUniquePlans"]["edges"]
            self.assertResponseNoErrors(response)
            self.assertEqual(len(response_plans), 5)

    def test_all_unique_plans_specs(self):
        projects = list()
        for i in range(5):
            project = ProjectFactory()
            projects.append(project)
            [
                FlatFactory(
                    project=project,
                    rooms=i + 1,
                    plan_code=f"{i}_flat#{j + 1}",
                    price=1000000 * (j + 1),
                )
                for j in range(5)
            ]

        query = """
                {
                    allUniquePlansSpecs {
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

        response = self.query(query)
        response_json = response.json()
        response_specs = response_json["data"]["allUniquePlansSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 3)
        for spec in response_specs:
            if spec["name"] == "city":
                self.assertEqual(len(spec["choices"]), 1)
            elif spec["name"] == "project":
                self.assertEqual(len(spec["choices"]), 5)
                projects_names = list(map(lambda x: x.name, projects))
                projects_ids = list(
                    map(lambda x: to_global_id(ProjectType.__name__, x.slug), projects)
                )
                for values in spec["choices"]:
                    self.assertTrue(values["label"] in projects_names)
                    self.assertTrue(values["value"] in projects_ids)
            elif spec["name"] == "rooms":
                self.assertEqual(len(spec["choices"]), 5)
                rooms_names = ["Студия", "1-ком.", "2-ком.", "3-ком.", "4-ком. и более"]
                rooms_values = ["0", "1", "2", "3", "4"]
                for values in spec["choices"]:
                    self.assertTrue(values["label"] in rooms_names)
                    self.assertTrue(values["value"] in rooms_values)

    def test_all_unique_plans_facets(self):
        projects = list()
        for i in range(5):
            project = ProjectFactory()
            projects.append(project)
            [
                FlatFactory(
                    project=project,
                    rooms=i + 1,
                    plan_code=f"{i}_flat#{j + 1}",
                    price=1000000 * (j + 1),
                )
                for j in range(5)
            ]

        query = """
                    {
                        allUniquePlansFacets {
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

        response = self.query(query)
        response_json = response.json()
        response_facets = response_json["data"]["allUniquePlansFacets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_facets["count"], 25)

        for facet in response_facets["facets"]:
            if facet["name"] == "city":
                self.assertEqual(len(facet["choices"]), 1)
            elif facet["name"] == "rooms":
                self.assertEqual(len(facet["choices"]), 4)
                for i in range(len(facet["choices"])):
                    self.assertEqual(str(i + 1), facet["choices"][i])
            elif facet["name"] == "project":
                projects_ids = list(
                    map(lambda x: to_global_id(ProjectType.__name__, x.slug), projects)
                )
                self.assertEqual(len(facet["choices"]), 5)
                for choice in facet["choices"]:
                    self.assertTrue(choice in projects_ids)


class GlobalFlatTest(BaseTestCase):
    def test_all_global_flats(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city_1)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        not_active_project = ProjectFactory(active=False)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        special_offers = [SpecialOfferFactory(is_active=i % 2 == 0) for i in range(6)]
        [ParkingPlaceFactory(project=project_1, building=building) for _ in range(3)]
        [CommercialPremiseFactory(project=project_1, building=building) for _ in range(3)]
        flats = [
            FlatFactory(
                project=project_1,
                building=building,
                section=section,
                floor=floor,
                special_offers=special_offers,
            )
            for _ in range(3)
        ] + [FlatFactory(project=project_2, special_offers=special_offers)]
        FlatFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.BOOKED,
        )
        FlatFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.SOLD,
        )
        FlatFactory(project=not_active_project, building=building, section=section, floor=floor)
        flats.append(
            FlatFactory(
                project=project_3,
                building=building,
                section=section,
                floor=floor,
                special_offers=special_offers,
            )
        )
        flat_ids = [to_global_id(GlobalFlatType.__name__, flat.pk) for flat in flats]
        flat_numbers = [flat.number for flat in flats]

        query = """
                {
                    allGlobalFlats {
                        totalCount
                        edges {
                            node {
                                id
                                number
                                building {
                                  windowViewPlanLotDisplay
                                  windowViewPlanLotPreview
                                }
                                windowView {
                                  ppoi
                                  windowviewangleSet {
                                      angle
                                }
                              }
                              specialOffers {
                                name
                                color
                                description
                                descriptionActive
                                startDate
                                finishDate
                                discountActive
                                discountValue
                                discountType
                                discountUnit
                                discountDescription
                                badgeIcon
                                badgeLabel
                              }
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allGlobalFlats"]["totalCount"], len(flats))
        self.assertEqual(len(response_flats), len(flats))
        for flat in response_flats:
            self.assertTrue(flat["node"]["id"] in flat_ids)
            self.assertTrue(flat["node"]["number"] in flat_numbers)
            self.assertIsNotNone(flat["node"]["building"]["windowViewPlanLotDisplay"])
            self.assertIsNotNone(flat["node"]["building"]["windowViewPlanLotPreview"])
            self.assertEqual(6 / 2, len(flat["node"]["specialOffers"]))

    def test_all_global_flats_with_has_balcony_or_loggia(self):
        feature = FeatureFactory(
            kind=FeatureTypeChoices.HAS_BALCONY_OR_LOGGIA, property_kind=[PropertyType.FLAT]
        )

        [FlatFactory(lounge_balcony=(i % 2 == 0)) for i in range(10)]
        query = """
                {
                    allGlobalFlats(features: ["%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
            """

        resp = self.query(query % feature.kind)
        self.assertResponseNoErrors(resp)
        resp_data = resp.json()["data"]
        self.assertEqual(5, len(resp_data["allGlobalFlats"]["edges"]))

    def test_all_global_flats_with_smart_house(self):
        feature = FeatureFactory(
            kind=FeatureTypeChoices.SMART_HOUSE, property_kind=[PropertyType.FLAT]
        )

        [FlatFactory(smart_house=(i % 2 == 0)) for i in range(10)]
        query = """
                {
                    allGlobalFlats(features: ["%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
            """

        resp = self.query(query % feature.kind)
        self.assertResponseNoErrors(resp)
        resp_data = resp.json()["data"]
        self.assertEqual(5, len(resp_data["allGlobalFlats"]["edges"]))

    def test_all_global_flats_with_euro_layout(self):
        feature = FeatureFactory(
            kind=FeatureTypeChoices.IS_EURO_LAYOUT, property_kind=[PropertyType.FLAT]
        )

        [FlatFactory(is_euro_layout=(i % 2 == 0)) for i in range(10)]
        query = """
                {
                    allGlobalFlats(features: ["%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
            """

        resp = self.query(query % feature.kind)
        self.assertResponseNoErrors(resp)
        resp_data = resp.json()["data"]
        self.assertEqual(5, len(resp_data["allGlobalFlats"]["edges"]))

    def test_all_global_flats_with_master_bedroom(self):
        feature = FeatureFactory(
            kind=FeatureTypeChoices.MASTER_BEDROOM, property_kind=[PropertyType.FLAT]
        )

        [FlatFactory(master_bedroom=(i % 2 == 0)) for i in range(10)]
        query = """
                {
                    allGlobalFlats(features: ["%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
            """

        resp = self.query(query % feature.kind)
        self.assertResponseNoErrors(resp)
        resp_data = resp.json()["data"]
        self.assertEqual(5, len(resp_data["allGlobalFlats"]["edges"]))

    def test_all_global_flats_with_params(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        building_id = to_global_id(BuildingType.__name__, buildings[0].id)
        [
            ParkingPlaceFactory(
                project=project,
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=0,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalFlats(building: "%s", rooms: ["0", "1"], priceMin: "%s", priceMax: "%s",
                             areaMin: "%s", areaMax: "%s") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        response = self.query(
            query
            % (
                building_id,
                str(flats[0].price),
                str(flats[5].price),
                str(flats[0].area),
                str(flats[5].area),
            )
        )

        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[0].number)

    def test_all_global_flats_with_floor(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        section = SectionFactory(building=building)
        floors = [FloorFactory(section=section) for _ in range(10)]
        flats = [
            FlatFactory(project=project, building=building, section=section, floor=floors[i])
            for i in range(10)
        ]

        query = """
                {
                    allGlobalFlats(floorMin: "%s", floorMax: "%s") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """
        response = self.query(query % (str(floors[4].number), str(floors[5].number)))
        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[4].number)
        self.assertEqual(response_flats[1]["node"]["number"], flats[5].number)

    def test_all_global_flats_with_facing(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        flats = [
            FlatFactory(
                project=project,
                building=building,
                section=section,
                floor=floor,
                facing=(i % 2 == 0),
            )
            for i in range(10)
        ]

        query = """
                {
                    allGlobalFlats(facing: true) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 5)
        for i in range(5):
            self.assertEqual(response_flats[i]["node"]["number"], flats[i * 2].number)

    def test_all_global_flats_with_project(self):
        projects = [ProjectFactory() for _ in range(2)]
        flats = [FlatFactory(project=projects[i % 2]) for i in range(6)]

        query = """
                {
                    allGlobalFlats(project: "%s") {
                        edges {
                            node {
                                number
                            }
                        }
                    }
                }
                """
        response = self.query(query % to_global_id(ProjectType.__name__, projects[0].slug))
        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 3)
        for i in range(3):
            self.assertEqual(response_flats[i]["node"]["number"], flats[i * 2].number)

    def test_all_global_flats_with_installment(self):
        project = ProjectFactory()
        flats = [FlatFactory(project=project, installment=i % 2 == 0) for i in range(10)]

        query = """
                {
                    allGlobalFlats(installment: true) {
                        edges {
                            node {
                                number
                            }
                        }
                    }
                }
                """
        response = self.query(query)
        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 5)
        for i in range(5):
            self.assertEqual(response_flats[i]["node"]["number"], flats[i * 2].number)

    def test_all_global_flats_with_block(self):
        block = LandingBlockFactory()
        flats = [FlatFactory() for _ in range(10)]

        block.flat_set.add(*flats[:3])
        query = """
                {
                    allGlobalFlats(landingBlock: %d) {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
                """
        response = self.query(query % block.id)
        self.assertResponseNoErrors(response)

        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]
        self.assertEqual(3, len(response_flats))
        self.assertEqual(
            [to_global_id(GlobalFlatType.__name__, f.id) for f in flats[:3]],
            [f["node"]["id"] for f in response_flats],
        )

    def test_all_global_lats_with_order(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        building_id = to_global_id(BuildingType.__name__, buildings[0].id)
        [
            ParkingPlaceFactory(
                project=project,
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=0,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalFlats(building: "%s", rooms: ["0", "1"], priceMin: "%s", priceMax: "%s",
                             areaMin: "%s", areaMax: "%s", orderBy: "-price") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        response = self.query(
            query
            % (
                building_id,
                str(flats[0].price),
                str(flats[5].price),
                str(flats[0].area),
                str(flats[5].area),
            )
        )

        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 2)
        self.assertEqual(response_flats[0]["node"]["number"], flats[4].number)
        self.assertEqual(response_flats[1]["node"]["number"], flats[0].number)

    def test_all_global_flats_with_ids(self):
        project = ProjectFactory()
        flats = [FlatFactory(project=project) for _ in range(9)]
        flats_ids = [to_global_id(GlobalFlatType.__name__, flat.pk) for flat in flats]

        query = """
                {
                    allGlobalFlats(id: ["%s", "%s", "%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        response = self.query(query % (flats_ids[0], flats_ids[4], flats_ids[8]))

        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 3)
        self.assertEqual(response_flats[0]["node"]["id"], flats_ids[0])
        self.assertEqual(response_flats[1]["node"]["id"], flats_ids[4])
        self.assertEqual(response_flats[2]["node"]["id"], flats_ids[8])

    def test_all_global_flats_completed(self):
        current_date = now().date()
        future_date = current_date + timedelta(days=93)
        past_date = current_date - timedelta(days=93)
        project = ProjectFactory()
        buildings = [
            BuildingFactory(
                project=project, built_year=date.year, ready_quarter=(date.month - 1 // 3) + 1
            )
            for date in [past_date, future_date]
        ]
        [
            ParkingPlaceFactory(
                project=project,
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=0,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalFlats(features: ["completed"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        content = json.loads(response.content)
        response_flats = content["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_flats), 6)
        for i, flat in enumerate(response_flats):
            self.assertEqual(response_flats[i]["node"]["number"], flats[i * 2].number)

    def test_all_global_flats_with_features(self):
        feature = FeatureFactory(kind=FeatureTypeChoices.FACING, property_kind=[PropertyType.FLAT])
        [FlatFactory(facing=i % 2) for i in range(10)]

        query = """
                {
                    allGlobalFlats(features: ["%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
            """

        resp = self.query(query % feature.kind)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]
        self.assertEqual(5, len(resp_data["allGlobalFlats"]["edges"]))

    def test_all_global_flats_with_special_offers(self):
        flats = [FlatFactory() for _ in range(9)]
        special_offers = [SpecialOfferFactory() for _ in range(3)]
        for i, flat in enumerate(flats):
            flat.specialoffer_set.add(special_offers[i % 3])

        query = """
                {
                    allGlobalFlats(specialOffers: ["%s"]) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
            """

        resp = self.query(query % special_offers[0].id)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]
        self.assertEqual(3, len(resp_data["allGlobalFlats"]["edges"]))

    def test_all_global_flats_specs(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        building_ids = [to_global_id(BuildingType.__name__, building.id) for building in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 5
        filter_features = [
            FeatureFactory(filter_show=True, property_kind=[PropertyType.FLAT]) for _ in range(5)
        ]
        [FeatureFactory(filter_show=False, property_kind=[PropertyType.FLAT]) for _ in range(6)]
        special_offers = [SpecialOfferFactory() for _ in range(3)]
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                special_offers=[special_offers[i % 3]],
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalFlatsSpecs {
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
                                icon
                                iconShow
                                description
                                mainFilterShow
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        content = json.loads(response.content)
        response_specs = content["data"]["allGlobalFlatsSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 18)
        self.assertEqual(response_specs[1]["name"], "building")
        for i in range(len(buildings)):
            self.assertEqual(response_specs[1]["choices"][i]["label"], buildings[i].name_display)
            self.assertEqual(response_specs[1]["choices"][i]["value"], building_ids[i])
        self.assertEqual(response_specs[2]["name"], "project")
        for i in range(len(projects)):
            self.assertEqual(response_specs[2]["choices"][i]["label"], projects[i].name)
            self.assertEqual(response_specs[2]["choices"][i]["value"], project_ids[i])
        self.assertEqual(response_specs[3]["name"], "price")
        self.assertEqual(response_specs[3]["range"]["min"], flats[0].price)
        self.assertEqual(response_specs[3]["range"]["max"], flats[-1].price)
        self.assertEqual(response_specs[4]["name"], "area")
        self.assertEqual(response_specs[4]["range"]["min"], flats[0].area)
        self.assertEqual(response_specs[4]["range"]["max"], flats[-1].area)
        self.assertEqual(response_specs[5]["name"], "completion_date")
        for i in range(len(buildings)):
            self.assertEqual(
                response_specs[5]["choices"][i]["label"],
                f"{buildings[i].ready_quarter} кв. {buildings[i].built_year}",
            )
            self.assertEqual(
                response_specs[5]["choices"][i]["value"],
                f"{buildings[i].built_year}-{buildings[i].ready_quarter}",
            )
        self.assertEqual(response_specs[7]["name"], "features")
        self.assertEqual(len(filter_features), len(response_specs[7]["choices"]))
        self.assertEqual(
            response_specs[7]["choices"][0]["value"], to_camel_case(filter_features[0].kind)
        )
        self.assertEqual(response_specs[7]["choices"][0]["label"], filter_features[0].name)
        self.assertEqual(response_specs[7]["choices"][0]["icon"], filter_features[0].icon.url)
        self.assertEqual(response_specs[7]["choices"][0]["iconShow"], filter_features[0].icon_show)
        self.assertEqual(
            response_specs[7]["choices"][0]["mainFilterShow"], filter_features[0].main_filter_show
        )
        self.assertEqual(
            response_specs[7]["choices"][0]["description"], filter_features[0].description
        )
        self.assertEqual(
            response_specs[7]["choices"][4]["value"], to_camel_case(filter_features[4].kind)
        )
        self.assertEqual(response_specs[7]["choices"][4]["label"], filter_features[4].name)
        self.assertEqual(
            response_specs[7]["choices"][4]["value"], to_camel_case(filter_features[4].kind)
        )
        self.assertEqual(response_specs[8]["name"], "special_offers")
        for i, offer in enumerate(special_offers):
            self.assertEqual(response_specs[8]["choices"][i]["label"], offer.name)
            self.assertEqual(response_specs[8]["choices"][i]["value"], str(offer.id))
        self.assertEqual(response_specs[9]["name"], "rooms")
        self.assertEqual(response_specs[9]["choices"][0]["label"], "Студия")
        self.assertEqual(response_specs[9]["choices"][0]["value"], "0")
        self.assertEqual(response_specs[9]["choices"][1]["label"], "1")
        self.assertEqual(response_specs[9]["choices"][1]["value"], "1")
        self.assertEqual(response_specs[9]["choices"][2]["label"], "2")
        self.assertEqual(response_specs[9]["choices"][2]["value"], "2")
        self.assertEqual(response_specs[9]["choices"][3]["label"], "3")
        self.assertEqual(response_specs[9]["choices"][3]["value"], "3")
        self.assertEqual(response_specs[9]["choices"][4]["label"], "4+")
        self.assertEqual(response_specs[9]["choices"][4]["value"], "4")
        self.assertEqual(response_specs[10]["name"], "floor")
        self.assertEqual(response_specs[10]["range"]["min"], floors[0].number)
        self.assertEqual(response_specs[10]["range"]["max"], floors[-1].number)

    def test_all_global_flats_facets(self):
        current_date = now().date()
        dates = [current_date - timedelta(days=93), current_date + timedelta(days=93)]
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [
            BuildingFactory(
                project=projects[i % 3],
                built_year=dates[i].year,
                ready_quarter=(dates[i].month - 1 // 3) + 1,
            )
            for i in range(2)
        ]
        building_ids = [to_global_id(BuildingType.__name__, building.id) for building in buildings]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        special_offers = [SpecialOfferFactory() for _ in range(3)]
        min_rooms = 0
        max_rooms = 5
        filter_features = [
            FeatureFactory(
                filter_show=True,
                property_kind=[PropertyType.FLAT],
                kind=FeatureTypeChoices.choices[i][0],
            )
            for i in range(5)
        ]
        [FeatureFactory(filter_show=False, property_kind=[PropertyType.FLAT]) for _ in range(6)]
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        flats = [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                facing=(i % 2 == 0),
                has_view=(i % 2 == 0),
                has_terrace=(i % 2 == 0),
                has_parking=(i % 2 == 0),
                is_duplex=(i % 2 == 0),
                corner_windows=(i % 2 == 0),
                has_high_ceiling=(i % 2 == 0),
                has_panoramic_windows=(i % 2 == 0),
                has_two_sides_windows=(i % 2 == 0),
                balconies_count=i % 3,
                loggias_count=i % 3,
                stores_count=i % 3,
                wardrobes_count=i % 3,
                installment=(i % 2 == 0),
                favorable_rate=(i % 2 == 0),
                frontage=(i % 2 == 0),
                preferential_mortgage=(i % 2 == 0),
                has_action_parking=(i % 2 == 0),
                promo_start=now() - timedelta(days=5 - i),
                special_offers=[special_offers[i % 3]],
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalFlatsFacets {
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
        response = self.query(query)
        content = json.loads(response.content)
        response_facets = content["data"]["allGlobalFlatsFacets"]["facets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_facets), 19)
        for facet in response_facets:
            if facet["name"] == "building":
                self.assertSetEqual(set(facet["choices"]), set(building_ids))
            elif facet["name"] == "facing":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "installment":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "project":
                for i in range(len(projects)):
                    self.assertEqual(facet["choices"][i], project_ids[i])
            elif facet["name"] == "price":
                self.assertEqual(facet["range"]["min"], flats[0].price)
                self.assertEqual(facet["range"]["max"], flats[-1].price)
            elif facet["name"] == "area":
                self.assertEqual(facet["range"]["min"], flats[0].area)
                self.assertEqual(facet["range"]["max"], flats[-1].area)
            elif facet["name"] == "completion_date":
                self.assertEqual(
                    facet["choices"],
                    [f"{building.built_year}-{building.ready_quarter}" for building in buildings],
                )
            elif facet["name"] == "action":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "rooms":
                rooms_set = {str(i) if i <= 4 else "4" for i in range(min_rooms, max_rooms + 1)}
                self.assertSetEqual(set(facet["choices"]), rooms_set)
            elif facet["name"] == "floor":
                self.assertEqual(facet["range"]["min"], floors[0].number)
                self.assertEqual(facet["range"]["max"], floors[-1].number)
            elif facet["name"] == "balconiesCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "loggiasCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "storesCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "wardrobesCount":
                self.assertSetEqual(set(facet["choices"]), {"0", "1", "2"})
            elif facet["name"] == "is_favorite":
                self.assertSetEqual(set(facet["choices"]), {"false"})
            elif facet["name"] == "features":
                self.assertSetEqual(
                    set(facet["choices"]), set(to_camel_case(feat.kind) for feat in filter_features)
                )
            elif facet["name"] == "special_offers":
                self.assertEqual(facet["choices"], [str(o.id) for o in special_offers])

    def test_global_flat(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=1 + i % 2,
                price=5000000 + 100000 * i,
                facing=True,
                has_high_ceiling=False,
            )
            for i in range(12)
        ]
        flat_id = to_global_id(GlobalFlatType.__name__, flats[0].id)

        feature_1 = FeatureFactory(kind=FeatureTypeChoices.FACING)
        FeatureFactory(kind=FeatureTypeChoices.HIGH_CEILING)

        query = """
                {
                    globalFlat(id: "%s") {
                        id
                        features {
                          name
                          icon
                          description
                        }
                    }
                }
                """

        res = self.query(query % flat_id)
        content = json.loads(res.content)["data"]["globalFlat"]

        self.assertResponseNoErrors(res)
        self.assertEqual(content["id"], flat_id)
        self.assertIsNotNone(content["features"])
        self.assertEqual(0, len(content["features"]))

    def test_global_flat_window_view(self):
        b = BuildingFactory()
        view_type = WindowViewTypeFactory(building=b)
        view = WindowViewFactory(type=view_type)
        [WindowViewAngleFactory(window_view=view) for _ in range(3)]
        mini_plan_point = MiniPlanPointFactory(type=view_type)
        [MiniPlanPointAngleFactory(mini_plan=mini_plan_point) for _ in range(4)]
        flat = FlatFactory(building=b, window_view=view, mini_plan_point=mini_plan_point)
        flat_id = to_global_id(GlobalFlatType.__name__, flat.id)

        query = """
                {
                    globalFlat(id: "%s") {
                        id
                        building {
                            windowViewPlanDisplay
                            windowViewPlanPreview
                        }
                        miniPlanPoint {
                          ppoi
                          miniplanpointangleSet {
                            angle
                          }
                        }
                        windowView {
                          ppoi
                          windowviewangleSet {
                            angle
                          }
                        }
                    }
                }
                """

        res = self.query(query % flat_id)
        content = json.loads(res.content)
        flat_data = content["data"]["globalFlat"]

        self.assertResponseNoErrors(res)
        self.assertEqual(flat_data["id"], flat_id)
        self.assertIsNotNone(flat_data["building"])
        self.assertIsNotNone(flat_data["building"]["windowViewPlanDisplay"])
        self.assertIsNotNone(flat_data["building"]["windowViewPlanPreview"])
        self.assertIsNotNone(flat_data["windowView"])
        self.assertEqual(flat_data["windowView"]["ppoi"], flat.window_view.ppoi)
        self.assertIsNotNone(flat_data["windowView"]["windowviewangleSet"])
        self.assertEqual(3, len(flat_data["windowView"]["windowviewangleSet"]))
        self.assertIsNotNone(flat_data["miniPlanPoint"])
        self.assertEqual(flat_data["miniPlanPoint"]["ppoi"], flat.mini_plan_point.ppoi)
        self.assertIsNotNone(flat_data["miniPlanPoint"]["miniplanpointangleSet"])
        self.assertEqual(4, len(flat_data["miniPlanPoint"]["miniplanpointangleSet"]))

    def test_all_global_flats_with_city(self):
        city_ids = []
        for _ in range(5):
            city = CityFactory()
            project = ProjectFactory(city=city)
            [FlatFactory(project=project) for _ in range(7)]
            city_ids.append(to_global_id(CityType.__name__, city.id))

        query = """
                query {
                    allGlobalFlats (city: "%s") {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        AWAITABLE_STATUS = 200
        AWAITABLE_FLATS_LEN = 7

        for city_id in city_ids:
            response = self.query(query % city_id)
            response_status = response.status_code
            response_json = response.json()
            response_flats = response_json["data"]["allGlobalFlats"]["edges"]

            self.assertResponseNoErrors(response)
            self.assertEqual(response_status, AWAITABLE_STATUS)
            self.assertEqual(len(response_flats), AWAITABLE_FLATS_LEN)

    def test_all_global_flats_infras(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        project_1 = ProjectFactory(city=city_1)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        [
            FlatFactory(project=project_1, building=building, section=section, floor=floor)
            for _ in range(3)
        ]
        first_infra = MainInfraFactory(project=project_1)
        first_infra_content = MainInfraContentFactory(main_infra=first_infra)
        [MainInfraContentFactory(main_infra=first_infra) for _ in range(5)]
        for _ in range(5):
            infra = MainInfraFactory(project=project_1)
            for _ in range(3):
                MainInfraContentFactory(main_infra=infra)

        query = """
                query {
                    allGlobalFlats {
                        edges {
                            node {
                                infra
                                infraText
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_flats = response_json["data"]["allGlobalFlats"]["edges"]

        for flat in response_flats:
            self.assertEqual(flat["node"]["infra"], first_infra.name)
            self.assertEqual(flat["node"]["infraText"], first_infra_content.value)

    def test_all_global_flats_first_payment(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        project_1 = ProjectFactory(city=city_1)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        flats = [
            FlatFactory(
                project=project_1,
                building=building,
                section=section,
                floor=floor,
                price=(i + 1) * 100000,
            )
            for i in range(3)
        ]
        offer = OfferFactory(
            amount=(100000, 900000),
            deposit=(10, 50),
            rate=(10, 50),
            term=(10, 50),
            type=MortgageType.RESIDENTIAL,
        )
        offer.projects.add(project_1)
        offer.save()

        query = """
                query {
                    allGlobalFlats {
                        edges { 
                            node {
                                firstPayment
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_flats = response_json["data"]["allGlobalFlats"]["edges"]

        for i in range(len(response_flats)):
            self.assertEqual(response_flats[i]["node"]["firstPayment"], flats[i].price * 0.1)

    def test_all_global_flats_building_total_floor(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        project_1 = ProjectFactory(city=city_1)
        building_1 = BuildingFactory(project=project_1)
        building_2 = BuildingFactory(project=project_1)
        section_1 = SectionFactory(building=building_1)
        section_2 = SectionFactory(building=building_2)
        section_3 = SectionFactory(building=building_1)
        floors_1 = [FloorFactory(section=section_1) for _ in range(15)]
        floors_2 = [FloorFactory(section=section_3) for _ in range(9)]
        [FloorFactory(section=section_2) for _ in range(11)]
        [
            FlatFactory(
                project=project_1,
                building=building_1,
                section=section_1,
                floor=floors_1[i],
                price=(i + 1) * 100000,
            )
            for i in range(3)
        ]

        query = """
                query {
                    allGlobalFlats {
                        edges { 
                            node {
                                buildingTotalFloor
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_flats = response_json["data"]["allGlobalFlats"]["edges"]
        self.assertResponseNoErrors(response)


    def test_min_mortgage(self):
        projects = []
        for i in range(5):
            project = ProjectFactory()
            projects.append(project)
            for j in range(5):
                FlatFactory(project=project, price=(j + i + 1) * 1000000)
                CommercialPremiseFactory(project=project, price=(j + i + 1) * 1000000)
        for project in projects:
            for _ in range(5):
                offer = OfferFactory(
                    amount=(100000, 900000),
                    deposit=(10, 50),
                    rate=(10, 50),
                    term=(10, 50),
                    type=MortgageType.RESIDENTIAL,
                )
                offer.projects.add(project)
                offer.save()
            for _ in range(5):
                offer = OfferFactory(
                    amount=(100000, 900000),
                    deposit=(10, 50),
                    rate=(10, 50),
                    term=(10, 50),
                    type=MortgageType.COMMERCIAL,
                )
                offer.projects.add(project)
                offer.save()

        offer_res = OfferFactory(
            amount=(100000, 5000000),
            deposit=(10, 50),
            rate=(10, 50),
            term=(10, 50),
            type=MortgageType.RESIDENTIAL,
        )
        offer_res.projects.add(projects[0])
        offer_res.save()
        offer_comm = OfferFactory(
            amount=(100000, 15000000),
            deposit=(10, 50),
            rate=(20, 50),
            term=(10, 50),
            type=MortgageType.COMMERCIAL,
        )
        offer_comm.projects.add(projects[0])
        offer_comm.save()

        query = """
                query {
                    allGlobalFlats {
                        edges {
                            node {
                                minMortgage
                                price
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_flats = response_json["data"]["allGlobalFlats"]["edges"]

        self.assertResponseNoErrors(response)

        flats_with_mortgage = 0
        for flat in response_flats:
            if flat["node"]["minMortgage"]:
                flats_with_mortgage += 1

        self.assertEqual(flats_with_mortgage, 25)


class GlobalParkingSpaceTest(BaseTestCase):
    def test_all_global_parking_spaces(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city_1)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        not_active_project = ProjectFactory(active=False)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        parking_spaces = [
            ParkingPlaceFactory(project=project_1, building=building, section=section, floor=floor)
            for _ in range(3)
        ] + [ParkingPlaceFactory(project=project_2)]
        ParkingPlaceFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.SOLD,
        )
        ParkingPlaceFactory(
            project=not_active_project, building=building, section=section, floor=floor
        )
        parking_spaces.append(
            ParkingPlaceFactory(project=project_3, building=building, section=section, floor=floor)
        )

        query = """
                {
                    allGlobalParkingSpaces {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """
        response = self.query(query)
        content = json.loads(response.content)
        res_parking_spaces = content["data"]["allGlobalParkingSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["allGlobalParkingSpaces"]["totalCount"], len(parking_spaces)
        )
        self.assertEqual(len(res_parking_spaces), len(parking_spaces))
        for i, parking_space in enumerate(parking_spaces):
            parking_space_id = to_global_id(GlobalParkingSpaceType.__name__, parking_space.pk)
            self.assertEqual(res_parking_spaces[i]["node"]["id"], parking_space_id)
            self.assertEqual(res_parking_spaces[i]["node"]["number"], parking_space.number)

    def test_all_global_parking_spaces_with_params(self):
        projects = [ProjectFactory() for _ in range(2)]
        buildings = [BuildingFactory(project=projects[i]) for i in range(2)]
        sections = [SectionFactory(building=buildings[i]) for i in range(2)]
        floors = [FloorFactory(section=sections[i]) for i in range(2)]
        parking_spaces = [
            ParkingPlaceFactory(
                project=projects[i % 2],
                building=buildings[i % 2],
                section=sections[i % 2],
                floor=floors[i % 2],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(8)
        ]

        project_id = to_global_id(ProjectType.__name__, projects[0].slug)
        floor_id = to_global_id(FloorType.__name__, floors[0].id)

        query = """
                {
                    allGlobalParkingSpaces (
                        project: "%s", floor: "%s", priceMin: "%s", priceMax: "%s",
                        areaMin: "%s", areaMax: "%s", completionDate: "%s", action: false
                    ) {
                        totalCount
                        edges {
                            node {
                                id
                                number
                                floor {
                                  id
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(
            query
            % (
                project_id,
                floor_id,
                str(parking_spaces[0].price),
                str(parking_spaces[3].price),
                str(parking_spaces[0].area),
                str(parking_spaces[1].area),
                f"{buildings[0].built_year}-{buildings[0].ready_quarter}",
            )
        )

        content = json.loads(response.content)
        res_parking_spaces = content["data"]["allGlobalParkingSpaces"]["edges"]
        parking_space_id = to_global_id(GlobalParkingSpaceType.__name__, parking_spaces[0].pk)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allGlobalParkingSpaces"]["totalCount"], 1)
        self.assertEqual(len(res_parking_spaces), 1)
        self.assertEqual(res_parking_spaces[0]["node"]["id"], parking_space_id)
        self.assertEqual(res_parking_spaces[0]["node"]["number"], parking_spaces[0].number)
        self.assertEqual(res_parking_spaces[0]["node"]["floor"]["id"], floor_id)

    def test_all_global_parking_spaces_specs(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 3
        parking_spaces = [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalParkingSpacesSpecs {
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
        response = self.query(query)
        content = json.loads(response.content)
        response_specs = content["data"]["allGlobalParkingSpacesSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 9)
        self.assertEqual(response_specs[2]["name"], "project")
        for i in range(len(projects)):
            self.assertEqual(response_specs[2]["choices"][i]["label"], projects[i].name)
            self.assertEqual(response_specs[2]["choices"][i]["value"], project_ids[i])
        self.assertEqual(response_specs[3]["name"], "price")
        self.assertEqual(response_specs[3]["range"]["min"], parking_spaces[0].price)
        self.assertEqual(response_specs[3]["range"]["max"], parking_spaces[-1].price)
        self.assertEqual(response_specs[4]["name"], "area")
        self.assertEqual(response_specs[4]["range"]["min"], parking_spaces[0].area)
        self.assertEqual(response_specs[4]["range"]["max"], parking_spaces[-1].area)
        self.assertEqual(response_specs[5]["name"], "completion_date")
        for i in range(len(buildings)):
            self.assertEqual(
                response_specs[5]["choices"][i]["label"],
                f"{buildings[i].ready_quarter} кв. {buildings[i].built_year}",
            )
            self.assertEqual(
                response_specs[5]["choices"][i]["value"],
                f"{buildings[i].built_year}-{buildings[i].ready_quarter}",
            )

    def test_all_global_parking_spaces_facets(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        min_rooms = 0
        max_rooms = 3
        parking_spaces = [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]
        [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                facing=(i % 2 == 0),
                has_view=(i % 2 == 0),
                has_terrace=(i % 2 == 0),
                has_parking=(i % 2 == 0),
                is_duplex=(i % 2 == 0),
                has_high_ceiling=(i % 2 == 0),
                has_panoramic_windows=(i % 2 == 0),
                has_two_sides_windows=(i % 2 == 0),
                balconies_count=i % 3,
                loggias_count=i % 3,
                stores_count=i % 3,
                wardrobes_count=i % 3,
                installment=(i % 2 == 0),
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalParkingSpacesFacets {
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

        response = self.query(query)
        content = json.loads(response.content)
        response_facets = content["data"]["allGlobalParkingSpacesFacets"]["facets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_facets), 12)
        for facet in response_facets:
            if facet["name"] == "project":
                for i in range(len(projects)):
                    self.assertEqual(facet["choices"][i], project_ids[i])
            elif facet["name"] == "price":
                self.assertEqual(facet["range"]["min"], parking_spaces[0].price)
                self.assertEqual(facet["range"]["max"], parking_spaces[-1].price)
            elif facet["name"] == "area":
                self.assertEqual(facet["range"]["min"], parking_spaces[0].area)
                self.assertEqual(facet["range"]["max"], parking_spaces[-1].area)
            elif facet["name"] == "completion_date":
                self.assertEqual(
                    facet["choices"],
                    [f"{building.built_year}-{building.ready_quarter}" for building in buildings],
                )
            elif facet["name"] == "action":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})


class GlobalCommercialSpaceTest(BaseTestCase):
    def test_all_global_commercial_spaces(self):
        site = Site.objects.first()
        city_1 = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city_1)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        not_active_project = ProjectFactory(active=False)
        building = BuildingFactory(project=project_1)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        commercial_spaces = [
            CommercialPremiseFactory(
                project=project_1, building=building, section=section, floor=floor
            )
            for _ in range(3)
        ] + [CommercialPremiseFactory(project=project_2)]
        commercial_apartments = [CommercialApartmentFactory() for _ in range(3)]
        CommercialPremiseFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.BOOKED,
        )
        CommercialPremiseFactory(
            project=project_1,
            building=building,
            section=section,
            floor=floor,
            status=PropertyStatus.SOLD,
        )
        CommercialPremiseFactory(
            project=not_active_project, building=building, section=section, floor=floor
        )
        commercial_spaces.append(
            CommercialPremiseFactory(
                project=project_3, building=building, section=section, floor=floor
            )
        )

        query = """
                {
                    allGlobalCommercialSpaces {
                        totalCount
                        edges {
                            node {
                                id
                                number
                                purposes {
                                  name
                                  icon
                                  description
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        content = json.loads(response.content)
        res_commercial_spaces = content["data"]["allGlobalCommercialSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["allGlobalCommercialSpaces"]["totalCount"],
            len(commercial_spaces) + len(commercial_apartments),
        )
        self.assertEqual(
            len(res_commercial_spaces), len(commercial_spaces) + len(commercial_apartments)
        )
        res_commercial_space_ids = [space["node"]["id"] for space in res_commercial_spaces]
        res_commercial_space_numbers = [space["node"]["number"] for space in res_commercial_spaces]
        for i, commercial_space in enumerate(commercial_spaces):
            self.assertIn(res_commercial_spaces[i]["node"]["id"], res_commercial_space_ids)
            self.assertIn(res_commercial_spaces[i]["node"]["number"], res_commercial_space_numbers)
        for i, commercial_space in enumerate(commercial_apartments):
            self.assertIn(res_commercial_spaces[i]["node"]["id"], res_commercial_space_ids)
            self.assertIn(res_commercial_spaces[i]["node"]["number"], res_commercial_space_numbers)

    def test_all_global_commercial_spaces_with_params(self):
        projects = [ProjectFactory() for _ in range(2)]
        buildings = [BuildingFactory(project=projects[i]) for i in range(2)]
        sections = [SectionFactory(building=buildings[i]) for i in range(2)]
        floors = [FloorFactory(section=sections[i]) for i in range(2)]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects[i % 2],
                building=buildings[i % 2],
                section=sections[i % 2],
                floor=floors[i % 2],
                price=5000000 + 100000 * i,
                area=50 + i,
                has_tenant=(i % 2 == 0),
            )
            for i in range(8)
        ]

        project_id = to_global_id(ProjectType.__name__, projects[0].slug)

        query = """
                {
                    allGlobalCommercialSpaces (
                        project: "%s", priceMin: "%s", priceMax: "%s",
                        areaMin: "%s", areaMax: "%s", completionDate: "%s",
                        action: false, hasTenant: true
                    ) {
                        totalCount
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        response = self.query(
            query
            % (
                project_id,
                str(commercial_spaces[0].price),
                str(commercial_spaces[3].price),
                str(commercial_spaces[0].area),
                str(commercial_spaces[1].area),
                f"{buildings[0].built_year}-{buildings[0].ready_quarter}",
            )
        )

        content = json.loads(response.content)
        res_commercial_spaces = content["data"]["allGlobalCommercialSpaces"]["edges"]
        commercial_space_id = to_global_id(
            GlobalCommercialSpaceType.__name__, commercial_spaces[0].pk
        )

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["allGlobalCommercialSpaces"]["totalCount"], 1)
        self.assertEqual(len(res_commercial_spaces), 1)
        self.assertEqual(res_commercial_spaces[0]["node"]["id"], commercial_space_id)
        self.assertEqual(res_commercial_spaces[0]["node"]["number"], commercial_spaces[0].number)

    def test_all_global_commercial_spaces_completed(self):
        current_date = now().date()
        future_date = current_date + timedelta(days=93)
        past_date = current_date - timedelta(days=93)
        project = ProjectFactory()
        buildings = [
            BuildingFactory(
                project=project, built_year=date.year, ready_quarter=(date.month - 1 // 3) + 1
            )
            for date in [past_date, future_date]
        ]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        query = """
                {
                    allCommercialSpaces(completed: true) {
                        edges {
                            node {
                                id
                                number
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query)
        content = json.loads(response.content)
        response_commercial_spaces = content["data"]["allCommercialSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_commercial_spaces), 6)
        for i, flat in enumerate(response_commercial_spaces):
            self.assertEqual(
                response_commercial_spaces[i]["node"]["number"], commercial_spaces[i * 2].number
            )

    def test_all_global_commercial_spaces_specs(self):
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(2)]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        property_purposes = [PropertyPurposeFactory() for _ in range(6)]
        special_offers = [SpecialOfferFactory() for _ in range(3)]
        min_rooms = 0
        max_rooms = 3
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=50 + i,
                purposes=property_purposes,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                special_offers=[special_offers[i % 3]],
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalCommercialSpacesSpecs {
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

        response = self.query(query)
        content = json.loads(response.content)
        response_specs = content["data"]["allGlobalCommercialSpacesSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 11)
        self.assertEqual(response_specs[2]["name"], "project")
        for i in range(len(projects)):
            self.assertEqual(response_specs[2]["choices"][i]["label"], projects[i].name)
            self.assertEqual(response_specs[2]["choices"][i]["value"], project_ids[i])
        self.assertEqual(response_specs[3]["name"], "price")
        self.assertEqual(response_specs[3]["range"]["min"], commercial_spaces[0].price)
        self.assertEqual(response_specs[3]["range"]["max"], commercial_spaces[-1].price)
        self.assertEqual(response_specs[4]["name"], "area")
        self.assertEqual(response_specs[4]["range"]["min"], commercial_spaces[0].area)
        self.assertEqual(response_specs[4]["range"]["max"], commercial_spaces[-1].area)
        self.assertEqual(response_specs[5]["name"], "completion_date")
        for i in range(len(buildings)):
            self.assertEqual(
                response_specs[5]["choices"][i]["label"],
                f"{buildings[i].ready_quarter} кв. {buildings[i].built_year}",
            )
            self.assertEqual(
                response_specs[5]["choices"][i]["value"],
                f"{buildings[i].built_year}-{buildings[i].ready_quarter}",
            )
        self.assertEqual(response_specs[8]["name"], "special_offers")
        self.assertEqual(response_specs[9]["name"], "purposes")
        for i in range(len(property_purposes)):
            self.assertEqual(int(response_specs[9]["choices"][i]["value"]), property_purposes[i].id)
            self.assertEqual(response_specs[9]["choices"][i]["label"], property_purposes[i].name)

    def test_all_global_commercial_spaces_facets(self):
        current_date = now().date()
        dates = [current_date - timedelta(days=93), current_date + timedelta(days=93)]
        projects = [ProjectFactory() for _ in range(3)]
        project_ids = [to_global_id(ProjectType.__name__, project.slug) for project in projects]
        buildings = [
            BuildingFactory(
                project=projects[i % 3],
                built_year=dates[i].year,
                ready_quarter=(dates[i].month - 1 // 3) + 1,
            )
            for i in range(2)
        ]
        sections = [SectionFactory(building=building) for building in buildings]
        floors = [FloorFactory(section=section) for section in sections]
        property_purposes = [PropertyPurposeFactory() for _ in range(6)]
        min_rooms = 0
        max_rooms = 3
        [
            ParkingPlaceFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                price=5000000 + 100000 * i,
                area=50 + i,
                promo_start=now() - timedelta(days=5 - i),
            )
            for i in range(12)
        ]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                price=5000000 + 100000 * i,
                area=50 + i,
                promo_start=now() - timedelta(days=5 - i),
                has_tenant=(i % 2 == 0),
                purposes=property_purposes,
            )
            for i in range(12)
        ]
        [
            FlatFactory(
                project=projects[i % 3],
                building=buildings[i % len(buildings)],
                section=sections[i % len(sections)],
                floor=floors[i % len(floors)],
                rooms=min_rooms + i % (max_rooms + 1),
                price=5000000 + 100000 * i,
                area=50 + i,
                facing=(i % 2 == 0),
                has_view=(i % 2 == 0),
                has_terrace=(i % 2 == 0),
                has_parking=(i % 2 == 0),
                is_duplex=(i % 2 == 0),
                has_high_ceiling=(i % 2 == 0),
                has_panoramic_windows=(i % 2 == 0),
                has_two_sides_windows=(i % 2 == 0),
                balconies_count=i % 3,
                loggias_count=i % 3,
                stores_count=i % 3,
                wardrobes_count=i % 3,
                installment=(i % 2 == 0),
            )
            for i in range(12)
        ]

        query = """
                {
                    allGlobalCommercialSpacesFacets {
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

        response = self.query(query)
        content = json.loads(response.content)
        response_facets = content["data"]["allGlobalCommercialSpacesFacets"]["facets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_facets), 17)
        for facet in response_facets:
            if facet["name"] == "project":
                for i in range(len(projects)):
                    self.assertEqual(facet["choices"][i], project_ids[i])
            elif facet["name"] == "price":
                self.assertEqual(facet["range"]["min"], commercial_spaces[0].price)
                self.assertEqual(facet["range"]["max"], commercial_spaces[-1].price)
            elif facet["name"] == "area":
                self.assertEqual(facet["range"]["min"], commercial_spaces[0].area)
                self.assertEqual(facet["range"]["max"], commercial_spaces[-1].area)
            elif facet["name"] == "completion_date":
                self.assertEqual(
                    facet["choices"],
                    [f"{building.built_year}-{building.ready_quarter}" for building in buildings],
                )
            elif facet["name"] == "action":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "hasTenant":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "completed":
                self.assertSetEqual(set(facet["choices"]), {"true", "false"})
            elif facet["name"] == "hasAuction":
                self.assertSetEqual(set(facet["choices"]), {"false"})
            if facet["name"] == "purposes":
                for i in range(len(property_purposes)):
                    self.assertEqual(int(facet["choices"][i]), property_purposes[i].id)

    def test_global_commercial_space(self):
        project = ProjectFactory()
        commercial_spaces = [
            CommercialPremiseFactory(project=project, price=5000000 + 500000 * i, area=50 + 10 * i)
            for i in range(5)
        ]
        commercial_space_ids = [
            to_global_id(GlobalCommercialSpaceType.__name__, n.id) for n in commercial_spaces
        ]

        query = """
                {
                    globalCommercialSpace (id: "%s") {
                        id
                    }
                }
                """

        response = self.query(query % commercial_space_ids[2])
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["globalCommercialSpace"]["id"], commercial_space_ids[2])


class SimilarFlatsTest(BaseTestCase):
    def test(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        flats = [
            FlatFactory(
                project=project,
                building=buildings[i % len(buildings)],
                rooms=1 + i % 2,
                price=5000000 + 100000 * i,
            )
            for i in range(12)
        ]
        flat_ids = [to_global_id(GlobalFlatType.__name__, n.id) for n in flats]

        query = """
                {
                    similarFlats(id: "%s", tab: "less_price") {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(4):
            res = self.query(query % flat_ids[8])
        content = json.loads(res.content)
        similar_flats = content["data"]["similarFlats"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(similar_flats), 4)
        self.assertEqual(similar_flats[0]["node"]["id"], flat_ids[0])
        self.assertEqual(similar_flats[1]["node"]["id"], flat_ids[2])
        self.assertEqual(similar_flats[2]["node"]["id"], flat_ids[4])
        self.assertEqual(similar_flats[3]["node"]["id"], flat_ids[6])

    def test_specs(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        flats = [
            FlatFactory(project=project, building=buildings[1], rooms=5, price=5000000 + 100000 * i)
            for i in range(12)
        ]
        flat_id = to_global_id(GlobalFlatType.__name__, flats[11].id)

        query = """
                query {
                    similarFlatsSpecs(id: "%s") {
                        label
                        value
                    }
                }
                """

        with self.assertNumQueries(6):
            response = self.query(query % flat_id)
        response_json = response.json()
        response_specs = response_json["data"]["similarFlatsSpecs"]

        self.assertResponseNoErrors(response)
        self.assertTrue(len(response_specs) in (1, 2))


class SimilarCommercialSpacesTest(BaseTestCase):
    def test(self):
        city_1 = CityFactory()
        projects_1 = [ProjectFactory(city=city_1) for _ in range(2)]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=projects_1[i % 2], price=5000000 + 500000 * i, area=50 + 5 * i
            )
            for i in range(5)
        ]
        commercial_space_ids = [
            to_global_id(GlobalCommercialSpaceType.__name__, n.id) for n in commercial_spaces
        ]

        city_2 = CityFactory()
        projects_2 = [ProjectFactory(city=city_2) for _ in range(2)]
        [
            CommercialPremiseFactory(
                project=projects_2[i % 2], price=5000000 + 500000 * i, area=50 + 5 * i
            )
            for i in range(5)
        ]

        query = """
                {
                    similarCommercialSpaces (id: "%s", tab: "larger_area") {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(4):
            response = self.query(query % commercial_space_ids[2])
        content = json.loads(response.content)
        res_similar = content["data"]["similarCommercialSpaces"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_similar), 1)
        self.assertEqual(res_similar[0]["node"]["id"], commercial_space_ids[4])

    def test_specs(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        commercial_spaces = [
            CommercialPremiseFactory(
                project=project,
                building=buildings[1],
                rooms=5,
                price=5000000 + 100000 * i,
                area=100,
            )
            for i in range(12)
        ]
        commercial_id = to_global_id(GlobalFlatType.__name__, commercial_spaces[11].id)

        query = """
                query {
                    similarCommercialSpacesSpecs(id: "%s") {
                        value
                        label
                    }
                }
                """

        with self.assertNumQueries(6):
            response = self.query(query % commercial_id)
        response_json = response.json()
        response_specs = response_json["data"]["similarCommercialSpacesSpecs"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_specs), 2)


class AllPropertyCardsTest(BaseTestCase):
    def test(self):
        [PropertyCardFactory() for _ in range(10)]

        query = """
                query {
                    allPropertyCards {
                        id
                        uptitle
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_cards = response_json["data"]["allPropertyCards"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_cards), 10)


class TestLayout(BaseTestCase):
    def test_layout(self):
        layout = LayoutFactory()
        flats = [FlatFactory() for _ in range(5)]
        sold_flats = [FlatFactory(status=PropertyStatus.SOLD) for _ in range(3)]

        layout.property_set.add(*flats)
        layout.property_set.add(*sold_flats)

        query = """
           query {
               layout (id: "%s") {
                   id
               }
           }
        """

        resp = self.query(query % to_global_id(LayoutObjectType.__name__, layout.id))
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["layout"]

        self.assertEqual(resp_data["id"], to_global_id(LayoutObjectType.__name__, layout.id))

    def test_all_layouts(self):
        projects = [ProjectFactory() for _ in range(3)]
        buildings = [BuildingFactory() for _ in range(3)]
        window_views = [WindowViewFactory() for _ in range(3)]
        layouts = [
            LayoutFactory(building=buildings[i], project=projects[i], type=PropertyType.FLAT)
            for i in range(3)
        ]

        offers = [
            OfferFactory(type=MortgageType.RESIDENTIAL, rate=NumericRange(3 + i, 5 + i))
            for i in range(10)
        ]
        for i, offer in enumerate(offers):
            offer.projects.add(projects[i % 3])
        flats = [
            FlatFactory(
                building=buildings[i % 3],
                layout=layouts[i % 3],
                window_view=window_views[i % 3],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        update_layouts()

        query = """
          query {
              allLayouts {
                  edges{
                    node{
                      id
                      name
                      area
                      price
                      maxFloor
                      minFloor
                      flatCount
                      hasSpecialOffers
                      firstPayment
                      firstFlatUrl
                      plan
                      planoplan
                      rooms
                      planHover
                      hasView
                      hasParking
                      hasActionParking
                      hasTerrace
                      hasHighCeiling
                      hasTwoSidesWindows
                      hasPanoramicWindows
                      isDuplex
                      installment
                      facing
                      frontage
                      type
                      minMortgage
                      minRate
                      floorPlan
                      floorPlanWidth
                      floorPlanHeight
                      floorPlanHover
                      maxDiscount
                      project {
                        name
                        apartments
                      }
                      building {
                        nameDisplay
                        builtYear
                        readyQuarter
                        windowViewPlanLotDisplay
                        windowViewPlanLotPreview
                      }
                      floor {
                        plan
                        planWidth
                        planHeight
                      }
                      windowView {
                        ppoi
                        windowviewangleSet {
                            angle
                        }
                      }
                    }
                  }
              }
          }
        """

        with self.assertNumQueries(3):
            resp = self.query(query)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["allLayouts"]["edges"]
        self.assertEqual(3, len(resp_data))
        for i, layout in enumerate(resp_data):
            self.assertEqual(layout["node"]["flatCount"], len(flats) / len(layouts))
            self.assertEqual(layout["node"]["minRate"], 3 + i)

    def test_all_layouts_with_filter(self):
        layouts = [LayoutFactory() for _ in range(3)]
        buildings = [BuildingFactory() for _ in range(3)]
        flats = [
            FlatFactory(
                building=buildings[i % 3],
                layout=layouts[i % 3],
                rooms=i % 4,
                price=5000000 + 100000 * i,
                area=50 + i,
            )
            for i in range(12)
        ]

        area_query = """
              query {
                  allLayouts(areaMin: "%s", areaMax: "%s") {
                      edges{
                        node{
                          id
                          flatCount
                        }
                      }
                  }
              }
            """

        resp = self.query(area_query % (flats[0].area, flats[3].area))
        self.assertResponseNoErrors(resp)

        building_query = """
              query {
                  allLayouts(building: "%s") {
                      edges{
                        node{
                          id
                          flatCount
                        }
                      }
                  }
              }
            """

        resp = self.query(building_query % (to_global_id(BuildingType.__name__, buildings[0].id)))
        self.assertResponseNoErrors(resp)

    @staticmethod
    def flats_count(resp_data):
        count = 0
        for layout in resp_data["data"]["allLayouts"]["edges"]:
            count += layout["node"]["flatCount"]
        return count


class PropertyConfigTest(BaseTestCase):
    def test_default(self):
        conf = PropertyConfig.objects.create(
            lot_form_title="Title", lot_form_description="Description"
        )

        query = """
          {
           propertyConfig {
             lotFormTitle
             lotFormDescription
           }
          }
        """

        resp = self.query(query)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["propertyConfig"]

        self.assertEqual(resp_data["lotFormTitle"], conf.lot_form_title)
        self.assertEqual(resp_data["lotFormDescription"], conf.lot_form_description)


class AllFurnishesTestCase(BaseTestCase):
    def test_default(self):
        furnishes = [FurnishFactory() for _ in range(6)]
        furnish_images = [FurnishImageFactory(furnish=furnishes[i % 6]) for i in range(12)]
        [FurnishPointFactory(image=furnish_images[i % 12]) for i in range(24)]

        query = """
        {
          allFurnishes {
            edges {
              node {
                name
                id
                vrLink
                description
                imageSet {
                    file
                    fileDisplay
                    filePreview
                    pointSet {
                        id
                        point
                        text
                        title
                    }
                }
              }
            }
          }
        }
        """

        with self.assertNumQueries(4):
            resp = self.query(query)
        resp_data = resp.json()

        self.assertResponseNoErrors(resp)
        self.assertEqual(len(resp_data["data"]["allFurnishes"]["edges"]), len(furnishes))
        for i, resp_furnish in enumerate(resp_data["data"]["allFurnishes"]["edges"]):
            self.assertEqual(
                resp_furnish["node"]["id"],
                to_global_id(FilteredFurnishType.__name__, furnishes[i].id),
            )

    def test_with_project(self):
        furnishes = [FurnishFactory() for _ in range(6)]
        furnish_images = [FurnishImageFactory(furnish=furnishes[i % 6]) for i in range(12)]
        [FurnishPointFactory(image=furnish_images[i % 12]) for i in range(24)]

        projects = [ProjectFactory() for _ in range(2)]
        for i in range(len(furnishes)):
            projects[i % 2].furnish_set.add(furnishes[i])

        query = """
        {
          allFurnishes(project: "%s") {
          edges {
            node {
              id
              name
              }
            }
          }
        }
        """

        resp = self.query(query % to_global_id(ProjectType.__name__, projects[0].slug))
        resp_data = resp.json()

        self.assertResponseNoErrors(resp)
        self.assertEqual(
            len(resp_data["data"]["allFurnishes"]["edges"]), projects[0].furnish_set.count()
        )


class ChangePropertyMutationTest(BaseTestCase):
    def test_default(self):
        flat = FlatFactory(views_count=0)

        query = """
                mutation {
                    changeProperty(
                        id: "%s"
                        hasViewed: true
                    ) {
                        ok
                    }
                }
        """

        resp = self.query(query % to_global_id(GlobalFlatType.__name__, flat.id))
        self.assertResponseNoErrors(resp)

        flat.refresh_from_db()
        self.assertEqual(flat.views_count, 1)

    def test_incorrect(self):
        query = """
                mutation {
                    changeProperty(
                        id: "666"
                        hasViewed: true
                    ) {
                        ok
                    }
                }
        """

        resp = self.query(query)
        resp_data = resp.json()

        self.assertResponseNoErrors(resp)
        self.assertFalse(resp_data["data"]["changeProperty"]["ok"])


class ListingActionTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(2)]
        actions = [ListingActionFactory(city=cities[i % 2]) for i in range(6)]

        query = """ {
            allListingActions(city: "%s") {
              edges {
                node {
                  title
                  description
                  imageDisplay
                  imagePreview
                  buttonName
                  buttonLink
                }
              }
            }
        }
        """

        resp = self.query(query % to_global_id(CityType.__name__, cities[0].id))
        resp_data = resp.json()

        self.assertResponseNoErrors(resp)

        self.assertEqual(len(actions) / 2, len(resp_data["data"]["allListingActions"]["edges"]))

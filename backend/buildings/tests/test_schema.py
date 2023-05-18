import json
from decimal import Decimal
from graphql_relay import to_global_id
from buildings.schema import BuildingType, SectionType
from buildings.constants import BuildingType
from buildings.tests.factories import BuildingFactory, SectionFactory, FloorFactory
from common.test_cases import BaseTestCase
from projects.schema import ProjectType
from projects.tests.factories import ProjectFactory
from properties.tests.factories import FlatFactory
from buildings.tasks import (
    calculate_building_fields_task,
    calculate_section_fields_task,
    calculate_floor_fields_task,
)
from properties.tests.factories import FurnishFactory, FurnishImageFactory


class AllBuildingsTest(BaseTestCase):
    def test_default(self):
        project = ProjectFactory()
        furnishes = [FurnishFactory() for _ in range(3)]
        [FurnishImageFactory(furnish=furnishes[i % 2]) for i in range(4)]
        buildings = [BuildingFactory(project=project) for _ in range(4)]
        for i, building in enumerate(buildings):
            building.furnish_set.set(furnishes)
            for j in range(1, 4):
                FlatFactory(project=project, building=building, price=100 * i + 10 * j, rooms=j)

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allBuildings { 
                        edges { 
                            node { 
                                name
                                number 
                                flats0MinPrice
                                flats1MinPrice
                                flats2MinPrice
                                flats3MinPrice
                                flats4MinPrice
                                furnishSet {
                                  id
                                  imageSet {
                                    id
                                    pointSet {
                                      id
                                    }
                                  }
                                }
                            } 
                        } 
                    } 
                }
                """

        with self.assertNumQueries(5):
            response = self.query(query)

        content = json.loads(response.content)
        res_buildings = content["data"]["allBuildings"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_buildings), len(buildings))
        print(len(res_buildings))

        for i, building in enumerate(buildings):
            res_building = res_buildings[i]["node"]
            self.assertEqual(res_building["name"], building.name)
            self.assertEqual(res_building["number"], building.number)
            self.assertEqual(Decimal(res_building["flats1MinPrice"]), Decimal(100 * i + 10))
            self.assertEqual(Decimal(res_building["flats2MinPrice"]), Decimal(100 * i + 20))
            self.assertEqual(Decimal(res_building["flats3MinPrice"]), Decimal(100 * i + 30))

            self.assertEqual(len(res_building["furnishSet"]), 3)
            for j in range(len(res_building["furnishSet"])):
                self.assertEqual(int(res_building["furnishSet"][j]["id"]), furnishes[j].id)

    def test_with_project(self):
        projects = [ProjectFactory() for _ in range(2)]
        buildings = [BuildingFactory(project=projects[i % 2]) for i in range(4)]
        project_id = to_global_id(ProjectType._meta.name, projects[0].slug)

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allBuildings(project: "%s") { 
                        edges { 
                            node { 
                                name
                                number
                            }
                        } 
                    } 
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query % project_id)

        content = json.loads(response.content)
        res_buildings = content["data"]["allBuildings"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_buildings), len(buildings) // 2)

        for i in range(len(buildings) // 2):
            self.assertEqual(res_buildings[i]["node"]["name"], buildings[i * 2].name)
            self.assertEqual(res_buildings[i]["node"]["number"], buildings[i * 2].number)

    def test_flats_count(self):
        project = ProjectFactory()
        for _ in range(2):
            building = BuildingFactory(project=project)
            for _ in range(5):
                section = SectionFactory(building=building)
                for i in range(7):
                    floor = FloorFactory(section=section, number=i + 1)
                    for _ in range(3):
                        FlatFactory(
                            section=section, floor=floor, building=building, project=project
                        )

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query {
                    allBuildings {
                        edges {
                            node {
                                flatsCount
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_buildings = response_json["data"]["allBuildings"]["edges"]

        for building in response_buildings:
            self.assertEqual(building["node"]["flatsCount"], 105)

    def test_with_kind(self):
        projects = [ProjectFactory() for _ in range(2)]
        buildings = [
            BuildingFactory(project=projects[i % 2], kind=BuildingType.RESIDENTIAL)
            for i in range(4)
        ]
        [BuildingFactory(project=projects[i % 2], kind=BuildingType.OFFICE) for i in range(4)]

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allBuildings(kind: ["%s"]) { 
                        edges { 
                            node { 
                                name
                                number
                            }
                        } 
                    } 
                }
                """

        response = self.query(query % buildings[0].kind)
        response_json = response.json()
        response_buildings = response_json["data"]["allBuildings"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_buildings), 4)


class AllSectionsTest(BaseTestCase):
    def test_default(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        sections = [SectionFactory(building=building) for _ in range(4)]
        for i, section in enumerate(sections):
            for j in range(1, 4):
                FlatFactory(project=project, section=section, price=100 * i + 10 * j, rooms=j)

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allSections { 
                        edges { 
                            node { 
                                name
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

        with self.assertNumQueries(2):
            response = self.query(query)

        content = json.loads(response.content)
        res_sections = content["data"]["allSections"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_sections), len(sections))

        for i, section in enumerate(sections):
            res_section = res_sections[i]["node"]
            self.assertEqual(res_section["name"], section.name)
            self.assertEqual(Decimal(res_section["flats1MinPrice"]), Decimal(100 * i + 10))
            self.assertEqual(Decimal(res_section["flats2MinPrice"]), Decimal(100 * i + 20))
            self.assertEqual(Decimal(res_section["flats3MinPrice"]), Decimal(100 * i + 30))

    def test_with_building(self):
        project = ProjectFactory()
        buildings = [BuildingFactory(project=project) for _ in range(2)]
        sections = [SectionFactory(building=buildings[i % 2]) for i in range(4)]
        building_id = to_global_id(BuildingType.__name__, buildings[0].id)

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allSections(building: "%s") { 
                        edges { 
                            node { 
                                name
                            } 
                        } 
                    } 
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query % building_id)

        content = json.loads(response.content)
        res_sections = content["data"]["allSections"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_sections), 2)

        for i in range(len(sections) // 2):
            self.assertEqual(res_sections[i]["node"]["name"], sections[i * 2].name)

    def test_flats_count(self):
        project = ProjectFactory()
        for _ in range(2):
            building = BuildingFactory(project=project)
            for _ in range(5):
                section = SectionFactory(building=building)
                for i in range(7):
                    floor = FloorFactory(section=section, number=i + 1)
                    for _ in range(3):
                        FlatFactory(
                            section=section, floor=floor, building=building, project=project
                        )

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query {
                    allSections {
                        edges {
                            node {
                                flatsCount
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_sections = response_json["data"]["allSections"]["edges"]

        for section in response_sections:
            self.assertEqual(section["node"]["flatsCount"], 21)


class AllFloorsTest(BaseTestCase):
    def test_default(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        section = SectionFactory(building=building)
        floors = [FloorFactory(section=section) for _ in range(4)]
        for i, floor in enumerate(floors):
            [FlatFactory(project=project, floor=floor, price=10 * i + j) for j in range(i)]

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allFloors { 
                        edges { 
                            node { 
                                number 
                                flatsCount
                                parkingCount
                                flatsMinPrice
                            } 
                        } 
                    } 
                }
                """
        with self.assertNumQueries(2):
            response = self.query(query)

        content = json.loads(response.content)
        res_floors = content["data"]["allFloors"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_floors), len(floors))

        for i, floor in enumerate(floors):
            res_floor = res_floors[i]["node"]
            self.assertEqual(res_floor["number"], floor.number)
            self.assertEqual(res_floor["flatsCount"], i)
            self.assertEqual(res_floor["flatsMinPrice"], "%.2f" % (i * 10) if i else None)

    def test_with_section(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        sections = [SectionFactory(building=building) for _ in range(2)]
        floors = [FloorFactory(section=sections[i % 2]) for i in range(4)]
        for i, floor in enumerate(floors):
            [FlatFactory(project=project, floor=floor) for _ in range(i)]
        section_id = to_global_id(SectionType._meta.name, sections[0].id)

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query { 
                    allFloors(section: "%s") { 
                        edges { 
                            node { 
                                number 
                                flatsCount
                            } 
                        } 
                    } 
                }
                """

        with self.assertNumQueries(2):
            response = self.query(query % section_id)

        content = json.loads(response.content)
        res_floors = content["data"]["allFloors"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(res_floors), len(floors) // 2)

        for i in range(len(floors) // 2):
            self.assertEqual(res_floors[i]["node"]["number"], floors[i * 2].number)
            self.assertEqual(res_floors[i]["node"]["flatsCount"], i * 2)

    def test_total_floor_annotations(self):
        project = ProjectFactory()
        for _ in range(2):
            building = BuildingFactory(project=project)
            for _ in range(5):
                section = SectionFactory(building=building)
                for i in range(7):
                    FloorFactory(section=section, number=i + 1)

        calculate_building_fields_task()
        calculate_section_fields_task()
        calculate_floor_fields_task()

        query = """
                query {
                    allBuildings {
                        edges {
                            node {
                                totalFloor
                                sectionSet {
                                    totalFloor
                                }
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_status = response.status_code
        response_json = response.json()
        response_buildings = response_json["data"]["allBuildings"]["edges"]

        AWAITABLE_STATUS = 200
        AWAITABLE_BUILDING_FLOORS = 7
        AWAITABLE_SECTION_FLOORS = 7

        self.assertResponseNoErrors(response)
        self.assertEqual(response_status, AWAITABLE_STATUS)
        for building in response_buildings:
            self.assertEqual(building["node"]["totalFloor"], AWAITABLE_BUILDING_FLOORS)
            sections = building["node"]["sectionSet"]
            for section in sections:
                self.assertEqual(section["totalFloor"], AWAITABLE_SECTION_FLOORS)

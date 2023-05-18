from graphql_relay import to_global_id
from buildings.tests.factories import BuildingFactory, SectionFactory, FloorFactory
from common.test_cases import BaseTestCase
from projects.tests.factories import ProjectFactory
from properties.schema import GlobalParkingSpaceType, GlobalFlatType
from properties.tests.factories import FlatFactory, ParkingPlaceFactory


class FavoriteMutationTest(BaseTestCase):
    def test_favorite(self):
        project = ProjectFactory()
        building = BuildingFactory(project=project)
        section = SectionFactory(building=building)
        floor = FloorFactory(section=section)
        parkings = [ParkingPlaceFactory(project=project, building=building) for _ in range(3)]
        flats = [
            FlatFactory(project=project, building=building, section=section, floor=floor)
            for _ in range(3)
        ]
        parking_id = to_global_id(GlobalParkingSpaceType.__name__, parkings[0].id)
        flat_id = to_global_id(GlobalFlatType.__name__, flats[0].id)

        add_query = """
                mutation {
                    createFavorite (id: "%s") {
                        status
                        count
                    }
                }
                """

        delete_query = """
                        mutation {
                            deleteFavorite (id: "%s") {
                                count
                                status
                            }
                        }
                        """

        parking_query = """
                        query {
                            allGlobalParkingSpaces (isFavorite: true) {
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

        flat_query = """
                        query {
                            allGlobalFlats (isFavorite: true) {
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

        response_add = self.query(add_query % parking_id)
        response_add_json = response_add.json()
        response_add_data = response_add_json["data"]["createFavorite"]
        self.assertEqual(response_add_data["status"], True)
        self.assertEqual(response_add_data["count"], 1)
        response_parking = self.query(parking_query)
        response_parking_json = response_parking.json()
        response_parking_total = response_parking_json["data"]["allGlobalParkingSpaces"][
            "totalCount"
        ]
        response_parking_data = response_parking_json["data"]["allGlobalParkingSpaces"]["edges"]
        self.assertEqual(response_parking_total, 1)
        self.assertEqual(response_parking_data[0]["node"]["id"], parking_id)

        response_add = self.query(add_query % flat_id)
        response_add_json = response_add.json()
        response_add_data = response_add_json["data"]["createFavorite"]
        self.assertEqual(response_add_data["status"], True)
        self.assertEqual(response_add_data["count"], 2)
        response_flat = self.query(flat_query)
        response_flat_json = response_flat.json()
        response_flat_total = response_flat_json["data"]["allGlobalFlats"]["totalCount"]
        response_flat_data = response_flat_json["data"]["allGlobalFlats"]["edges"]
        self.assertEqual(response_flat_total, 1)
        self.assertEqual(response_flat_data[0]["node"]["id"], flat_id)

        response_add = self.query(add_query % parking_id)
        response_add_json = response_add.json()
        response_add_data = response_add_json["data"]["createFavorite"]
        self.assertEqual(response_add_data["status"], False)
        self.assertEqual(response_add_data["count"], 2)
        response_parking = self.query(parking_query)
        response_parking_json = response_parking.json()
        response_parking_total = response_parking_json["data"]["allGlobalParkingSpaces"][
            "totalCount"
        ]
        response_parking_data = response_parking_json["data"]["allGlobalParkingSpaces"]["edges"]
        self.assertEqual(response_parking_total, 1)
        self.assertEqual(response_parking_data[0]["node"]["id"], parking_id)

        response_add = self.query(add_query % flat_id)
        response_add_json = response_add.json()
        response_add_data = response_add_json["data"]["createFavorite"]
        self.assertEqual(response_add_data["status"], False)
        self.assertEqual(response_add_data["count"], 2)
        response_flat = self.query(flat_query)
        response_flat_json = response_flat.json()
        response_flat_total = response_flat_json["data"]["allGlobalFlats"]["totalCount"]
        response_flat_data = response_flat_json["data"]["allGlobalFlats"]["edges"]
        self.assertEqual(response_flat_total, 1)
        self.assertEqual(response_flat_data[0]["node"]["id"], flat_id)

        response_delete = self.query(delete_query % parking_id)
        response_delete_json = response_delete.json()
        response_delete_data = response_delete_json["data"]["deleteFavorite"]
        self.assertEqual(response_delete_data["status"], True)
        self.assertEqual(response_delete_data["count"], 1)
        response_parking = self.query(parking_query)
        response_parking_json = response_parking.json()
        response_parking_total = response_parking_json["data"]["allGlobalParkingSpaces"][
            "totalCount"
        ]
        response_parking_data = response_parking_json["data"]["allGlobalParkingSpaces"]["edges"]
        self.assertEqual(response_parking_total, 0)
        self.assertEqual(response_parking_data, [])

        response_delete = self.query(delete_query % flat_id)
        response_delete_json = response_delete.json()
        response_delete_data = response_delete_json["data"]["deleteFavorite"]
        self.assertEqual(response_delete_data["status"], True)
        self.assertEqual(response_delete_data["count"], 0)
        response_flat = self.query(flat_query)
        response_flat_json = response_flat.json()
        response_flat_total = response_flat_json["data"]["allGlobalFlats"]["totalCount"]
        response_flat_data = response_flat_json["data"]["allGlobalFlats"]["edges"]
        self.assertEqual(response_flat_total, 0)
        self.assertEqual(response_flat_data, [])

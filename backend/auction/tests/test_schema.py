from graphql_relay import to_global_id

from common.test_cases import BaseTestCase
from projects.tests.factories import ProjectFactory
from properties.schema import GlobalCommercialSpaceType
from properties.tests.factories import CommercialPremiseFactory
from .factories import AuctionFactory


class AuctionTestCase(BaseTestCase):
    def test_commercial_space(self):
        commercial = [CommercialPremiseFactory() for _ in range(3)]
        auction = AuctionFactory(
            is_active=True,
            property_object=commercial[0],
            start_price=5_000_000,
            bet_count=3,
            step=100_000,
        )
        commercial_ids = [
            to_global_id(GlobalCommercialSpaceType.__name__, c.id) for c in commercial
        ]

        query = """
                {
                    globalCommercialSpace (id: "%s") {
                        id
                        hasAuction
                        auction {
                          startPrice
                          start
                          end
                          betCount
                          currentPrice
                          link
                          step
                        }
                    }
                }
                """

        resp = self.query(query % commercial_ids[0])
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["globalCommercialSpace"]
        self.assertEqual(resp_data["id"], commercial_ids[0])
        self.assertEqual(resp_data["hasAuction"], True)
        self.assertIsNotNone(resp_data["auction"])
        self.assertEqual(resp_data["auction"]["startPrice"], auction.start_price)
        self.assertEqual(resp_data["auction"]["betCount"], auction.bet_count)
        self.assertEqual(resp_data["auction"]["step"], auction.step)
        self.assertEqual(
            resp_data["auction"]["currentPrice"],
            auction.start_price + auction.step * auction.bet_count,
        )

        query = """
                {
                    globalCommercialSpace (id: "%s") {
                        id
                        hasAuction
                        auction {
                          startPrice
                          start
                          end
                          betCount
                          currentPrice
                          link
                        }
                    }
                }
                """

        resp = self.query(query % commercial_ids[2])
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["globalCommercialSpace"]
        self.assertEqual(resp_data["id"], commercial_ids[2])
        self.assertEqual(resp_data["hasAuction"], False)

    def test_all_global_commercial_spaces(self):
        commercial = [CommercialPremiseFactory() for _ in range(10)]
        for i in range(3):
            AuctionFactory(property_object=commercial[i])

        query = """
                {
                    allGlobalCommercialSpaces(hasAuction: true) {
                        totalCount
                        edges {
                            node {
                                id
                                number
                                auction {
                                  startPrice
                                  step
                                  start
                                  end
                                  betCount
                                  currentPrice
                                  isCurrent
                                }
                            }
                        }
                    }
                }
                """

        resp = self.query(query)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["allGlobalCommercialSpaces"]
        self.assertEqual(3, resp_data["totalCount"])
        for comm in resp_data["edges"]:
            self.assertIsNotNone(comm["node"]["auction"])

    def test_similar_comericlial_spaces(self):
        p = ProjectFactory()
        commercial = [
            CommercialPremiseFactory(project=p, area=50 + i, price=5_000_000 + i) for i in range(3)
        ]
        AuctionFactory(is_active=True, property_object=commercial[0])
        commercial_ids = [
            to_global_id(GlobalCommercialSpaceType.__name__, c.id) for c in commercial
        ]

        query = """
                {
                    similarCommercialSpaces (id: "%s", tab: "larger_area") {
                        edges {
                            node {
                                id
                                hasAuction
                            }
                        }
                    }
                }
                """

        resp = self.query(query % commercial_ids[0])
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["similarCommercialSpaces"]["edges"]
        self.assertEqual(2, len(resp_data))
        self.assertEqual(resp_data[0]["node"]["id"], commercial_ids[1])
        self.assertEqual(resp_data[1]["node"]["id"], commercial_ids[2])

    def test_notification_wrong_data(self):
        query = """
                mutation {
                    auctionNotification(input: {
                        name: "name"
                        phone: "wrong phone"
                        email: "email.ru"
                        auction: 999
                        lotLink: "not link"
                    }) {
                        ok
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(1):
            resp = self.query(query)

        self.assertResponseNoErrors(resp)
        content = resp.json()
        self.assertEqual(content["data"]["auctionNotification"]["ok"], False)
        self.assertEqual(len(content["data"]["auctionNotification"]["errors"]), 4)
        self.assertEqual(content["data"]["auctionNotification"]["errors"][0]["field"], "phone")
        self.assertEqual(content["data"]["auctionNotification"]["errors"][1]["field"], "email")
        self.assertEqual(content["data"]["auctionNotification"]["errors"][2]["field"], "auction")
        self.assertEqual(content["data"]["auctionNotification"]["errors"][3]["field"], "lot_link")

    def test_notification_correct_data(self):
        auction = AuctionFactory()
        query = """
                mutation {
                    auctionNotification(input: {
                        name: "name"
                        phone: "+79999999999"
                        email: "e@mail.ru"
                        auction: %d
                        lotLink: "https://google.com/"
                    }) {
                        ok
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            resp = self.query(query % auction.id)

        self.assertResponseNoErrors(resp)
        content = resp.json()
        self.assertEqual(content["data"]["auctionNotification"]["ok"], True)

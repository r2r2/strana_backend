import json
from decimal import Decimal
from django.contrib.sites.models import Site
from graphql_relay import to_global_id
from cities.tests.factories import CityFactory, SiteFactory
from cities.schema import CityType
from common.test_cases import BaseTestCase
from projects.schema import ProjectType
from projects.tests.factories import ProjectFactory
from properties.tests.factories import CommercialPremiseFactory, FlatFactory
from ..constants import MortgageType
from ..schema import OfferType, ProgramType
from .factories import (
    BankFactory,
    OfferFactory,
    ProgramFactory,
    MortgagePageFactory,
    MortgageAdvantageFactory,
    MortgageInstrumentFactory,
    MortgagePageFormFactory,
)


class TestMortgagePage(BaseTestCase):
    def test_default(self):
        site = Site.objects.first()
        form = MortgagePageFormFactory()
        page = MortgagePageFactory(site=site, form=form)
        advantages = [MortgageAdvantageFactory(page=page) for _ in range(3)]
        instruments = [MortgageInstrumentFactory(page=page) for _ in range(3)]

        query = """
                query {
                    mortgagePage {
                        id
                        title
                        advantages {
                            id
                            title
                        }
                        instruments {
                            id
                            title
                        }
                        form {
                            title
                        }
                    }
                }
                """
        with self.assertNumQueries(3):
            res = self.query(query)
            content = json.loads(res.content)
            res_page = content["data"]["mortgagePage"]

            self.assertResponseNoErrors(res)
            self.assertEqual(res_page["title"], page.title)
            self.assertEqual(len(res_page["advantages"]), len(advantages))
            for i, advantage in enumerate(res_page["advantages"]):
                self.assertEqual(advantage["title"], advantages[i].title)
            self.assertEqual(len(res_page["instruments"]), len(instruments))
            for i, instrument in enumerate(res_page["instruments"]):
                self.assertEqual(instrument["title"], instruments[i].title)
            self.assertEqual(res_page["form"]["title"], form.title)

    def test_city_filter(self):
        site_1 = Site.objects.first()
        city_1 = CityFactory()
        city_1.site = site_1
        city_1.save()
        form_1 = MortgagePageFormFactory()
        page_1 = MortgagePageFactory(site=site_1, form=form_1)
        [MortgageAdvantageFactory(page=page_1) for _ in range(3)]
        [MortgageInstrumentFactory(page=page_1) for _ in range(3)]
        site_2 = SiteFactory()
        city_2 = CityFactory()
        city_2.site = site_2
        city_2.save()
        form_2 = MortgagePageFormFactory()
        page_2 = MortgagePageFactory(site=site_2, form=form_2)
        advantages_2 = [MortgageAdvantageFactory(page=page_2) for _ in range(4)]
        instruments_2 = [MortgageInstrumentFactory(page=page_2) for _ in range(4)]

        query = """
                query {
                    mortgagePage (city: "%s") {
                        id
                        title
                        advantages {
                            id
                            title
                        }
                        instruments {
                            id
                            title
                        }
                        form {
                            title
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(query % to_global_id(CityType.__name__, city_2.id))
        content = json.loads(res.content)
        res_page = content["data"]["mortgagePage"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_page["title"], page_2.title)
        self.assertEqual(len(res_page["advantages"]), len(advantages_2))
        for i, advantage in enumerate(res_page["advantages"]):
            self.assertEqual(advantage["title"], advantages_2[i].title)
        self.assertEqual(len(res_page["instruments"]), len(instruments_2))
        for i, instrument in enumerate(res_page["instruments"]):
            self.assertEqual(instrument["title"], instruments_2[i].title)
        self.assertEqual(res_page["form"]["title"], form_2.title)


class TestAllOffers(BaseTestCase):
    def test_default(self):
        programs = [ProgramFactory() for _ in range(4)]
        offers = [OfferFactory(program=programs[i // 4 % 4]) for i in range(16)]
        [
            OfferFactory(is_active=False, program=programs[i % 4])
            for i in range(4)
        ]
        query = """
                {
                    allOffers {
                        edges {
                            node {
                                id
                                type
                                program {
                                    name
                                }
                                minDeposit
                                minRate
                                maxTerm
                                payment
                                subsPayment
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_offers = content["data"]["allOffers"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_offers), len(offers))
        for i, offer in enumerate(offers):
            self.assertEqual(
                res_offers[i]["node"]["id"], to_global_id(OfferType.__name__, offer.id)
            )
            self.assertIsNone(res_offers[i]["node"]["payment"])
            self.assertIsNone(res_offers[i]["node"]["subsPayment"])

    def test_with_params(self):
        cities = [CityFactory(), CityFactory(), None]
        programs = [ProgramFactory() for _ in range(4)]
        offers = [
            OfferFactory(
                type=MortgageType.choices[i % 2][0],
                program=programs[i // 4 % 4],
                city=cities[i % 3],
                amount=((i % 4) * 10000 + 10000, (i % 4) * 20000 + 20000),
                deposit=(Decimal(i % 8), Decimal(i % 8 + 10)),
                rate=(Decimal(i % 8), Decimal(i % 8 + 10)),
                term=(Decimal(i % 8), Decimal(i % 8 + 10)),
                subs_rate=(Decimal(1), Decimal(2)),
                subs_term=(Decimal(1), Decimal(2)),
            )
            for i in range(16)
        ]

        [
            OfferFactory(is_active=False, program=programs[i % 4])
            for i in range(4)
        ]

        query = """
                {
                    allOffers (city: "%s", type: "%s", program: "%s", price: %s, term: %s, deposit: %s) {
                        edges {
                            node {
                                id
                                type
                                program {
                                    name
                                }
                                minDeposit
                                minRate
                                maxTerm
                                payment
                                subsPayment
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(
                query
                % (
                    to_global_id(CityType.__name__, cities[0].id),
                    MortgageType.COMMERCIAL,
                    to_global_id(ProgramType.__name__, programs[1].id),
                    50000,
                    10,
                    8,
                )
            )
        content = json.loads(res.content)
        res_offers = content["data"]["allOffers"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_offers), 1)
        self.assertEqual(
            res_offers[0]["node"]["id"], to_global_id(OfferType.__name__, offers[6].id)
        )
        self.assertIsNotNone(res_offers[0]["node"]["payment"])
        self.assertIsNotNone(res_offers[0]["node"]["subsPayment"])


class TestAllOffersSpecs(BaseTestCase):
    def test_default(self):
        cities = [CityFactory(), CityFactory(), None]
        projects = [ProjectFactory() for i in range(4)]
        flats = [FlatFactory(project=projects[i], price=(i + 1) * 1000000) for i in range(4)]
        programs = [ProgramFactory(name=f"Program {i}") for i in range(4)]
        offers = [
            OfferFactory(
                type=MortgageType.choices[i % 2][0],
                program=programs[i // 4 % 4],
                city=cities[i % 3],
                amount=((i % 4) * 10000 + 10000, (i % 4) * 20000 + 20000),
                deposit=(Decimal(i % 8), Decimal(i % 8 + 10)),
                rate=(Decimal(i % 8), Decimal(i % 8 + 10)),
                term=(Decimal(i % 8), Decimal(i % 8 + 10)),
            )
            for i in range(16)
        ]
        for i in range(4):
            offers[i * 5].projects.add(projects[i])
        [
            OfferFactory(is_active=False, program=programs[i % 4])
            for i in range(4)
        ]

        query = """
                query {
                    allOffersSpecs (project: ["%s"], city: "%s", type: "%s") {
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

        with self.assertNumQueries(8):
            res = self.query(
                query
                % (
                    to_global_id(ProjectType.__name__, projects[2].slug),
                    to_global_id(CityType.__name__, cities[1].id),
                    MortgageType.COMMERCIAL,
                )
            )
        content = json.loads(res.content)
        res_specs = content["data"]["allOffersSpecs"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_specs[0]["name"], "type")
        for i, type in enumerate(res_specs[0]["choices"]):
            self.assertEqual(type["value"], MortgageType.choices[i][0])
            self.assertEqual(type["label"], MortgageType.choices[i][1])
        self.assertEqual(res_specs[1]["name"], "program")
        self.assertEqual(len(res_specs[1]["choices"]), 1)
        self.assertEqual(
            res_specs[1]["choices"][0]["value"], to_global_id(ProgramType.__name__, programs[2].id)
        )
        self.assertEqual(res_specs[1]["choices"][0]["label"], programs[2].name)
        self.assertEqual(res_specs[2]["name"], "deposit")
        self.assertEqual(res_specs[2]["range"]["min"], offers[10].deposit[0])
        self.assertEqual(res_specs[2]["range"]["max"], 90)
        self.assertEqual(res_specs[3]["name"], "rate")
        self.assertEqual(res_specs[3]["range"]["min"], offers[10].rate[0])
        self.assertEqual(res_specs[3]["range"]["max"], offers[10].rate[1])
        self.assertEqual(res_specs[4]["name"], "term")
        self.assertEqual(res_specs[4]["range"]["min"], offers[10].term[0])
        self.assertEqual(res_specs[4]["range"]["max"], offers[10].term[1])
        self.assertEqual(res_specs[5]["name"], "project")
        self.assertEqual(len(res_specs[5]["choices"]), 1)
        self.assertEqual(
            res_specs[5]["choices"][0]["value"],
            to_global_id(ProjectType.__name__, projects[2].slug),
        )
        self.assertEqual(res_specs[5]["choices"][0]["label"], projects[2].name)
        self.assertEqual(res_specs[6]["name"], "city")
        self.assertEqual(len(res_specs[6]["choices"]), 1)
        self.assertEqual(
            res_specs[6]["choices"][0]["value"], to_global_id(CityType.__name__, cities[1].id)
        )
        self.assertEqual(res_specs[6]["choices"][0]["label"], cities[1].name)
        self.assertEqual(res_specs[7]["name"], "price")
        self.assertEqual(res_specs[7]["range"]["min"], flats[0].price)
        self.assertEqual(res_specs[7]["range"]["max"], flats[3].price)


class TestAllOffersFacets(BaseTestCase):
    def test_default(self):
        cities = [CityFactory(), CityFactory(), None]
        projects = [ProjectFactory() for i in range(4)]
        flats = [
            CommercialPremiseFactory(project=projects[i], price=(i + 1) * 1000000) for i in range(4)
        ]
        programs = [ProgramFactory() for _ in range(4)]
        offers = [
            OfferFactory(
                type=MortgageType.choices[i % 2][0],
                program=programs[i // 4 % 4],
                city=cities[i % 3],
                amount=((i % 4) * 10000 + 10000, (i % 4) * 20000 + 20000),
                deposit=(Decimal(i % 8), Decimal(i % 8 + 10)),
                rate=(Decimal(i % 8), Decimal(i % 8 + 10)),
                term=(Decimal(i % 8), Decimal(i % 8 + 10)),
                subs_rate=(Decimal(i % 2), Decimal(i % 2 + 2)),
                subs_term=(Decimal(i % 2), Decimal(i % 2 + 2)),
            )
            for i in range(16)
        ]
        for i in range(4):
            offers[i * 5].projects.add(projects[i])

        [
            OfferFactory(is_active=False, program=programs[i % 4])
            for i in range(4)
        ]

        query = """
                query {
                    allOffersFacets (type: "%s") {
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
        with self.assertNumQueries(10):
            res = self.query(query % MortgageType.COMMERCIAL)
        content = json.loads(res.content)
        res_facets = content["data"]["allOffersFacets"]["facets"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_facets[0]["name"], "type")
        self.assertSetEqual(set(res_facets[0]["choices"]), set(dict(MortgageType.choices).keys()))
        self.assertEqual(res_facets[1]["name"], "program")
        self.assertSetEqual(
            set(res_facets[1]["choices"]),
            set([to_global_id(ProgramType.__name__, p.id) for p in programs]),
        )
        self.assertEqual(res_facets[2]["name"], "deposit")
        self.assertEqual(res_facets[2]["range"]["min"], offers[0].deposit[0])
        self.assertEqual(res_facets[2]["range"]["max"], 90)
        self.assertEqual(res_facets[3]["name"], "rate")
        self.assertEqual(res_facets[3]["range"]["min"], offers[0].rate[0])
        self.assertEqual(res_facets[3]["range"]["max"], offers[6].rate[1])
        self.assertEqual(res_facets[4]["name"], "term")
        self.assertEqual(res_facets[4]["range"]["min"], offers[0].term[0])
        self.assertEqual(res_facets[4]["range"]["max"], offers[6].term[1])
        self.assertEqual(res_facets[5]["name"], "project")
        self.assertSetEqual(
            set(res_facets[5]["choices"]),
            set([to_global_id(ProjectType.__name__, p.slug) for p in projects[::2]]),
        )
        self.assertEqual(res_facets[6]["name"], "city")
        self.assertSetEqual(
            set(res_facets[6]["choices"]),
            set([to_global_id(CityType.__name__, c.id) for c in cities[:2]]),
        )


class TestAllBanks(BaseTestCase):
    def test_default(self):
        banks = [BankFactory() for _ in range(4)]

        query = """
                query {
                    allBanks {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(1):
            res = self.query(query)
        content = json.loads(res.content)
        res_banks = content["data"]["allBanks"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_banks), 0)
        for i, bank in enumerate(res_banks):
            self.assertEqual(bank["node"]["name"], banks[i].name)
import json
from django.contrib.sites.models import Site
from graphql_relay import to_global_id
from cities.schema import CityType
from cities.tests.factories import CityFactory, MetroLineFactory, MetroFactory, TransportFactory
from common.test_cases import BaseTestCase
from mortgage.constants import MortgageType
from mortgage.tests.factories import OfferFactory, BankFactory
from projects.tasks import calculate_project_fields_task
from projects.tests.factories import (
    ProjectFactory,
    ProjectGallerySlideFactory,
    ProjectAdvantageFactory,
    ProjectIdeologyFactory,
    ProjectIdeologyCardFactory,
    ProjectAdvantageSlideFactory,
    ProjectWebcamFactory,
    ProjectLabelFactory,
)
from properties.tests.factories import (
    FlatFactory,
    FurnishFactory,
    FurnishImageFactory,
    FurnishPointFactory,
    CommercialPremiseFactory,
)
from ..constants import ProjectStatusType


class ProjectTest(BaseTestCase):
    def test_all_projects(self):
        site = Site.objects.first()
        city = CityFactory(site=site)
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city)
        project_2 = ProjectFactory()
        ProjectFactory(active=False)
        ProjectFactory(city=city_2)
        calculate_project_fields_task()

        query = """
                query {
                    allProjects {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        content = json.loads(response.content)
        response_projects = content["data"]["allProjects"]["edges"]
        response_project_1 = response_projects[0]["node"]
        response_project_2 = response_projects[1]["node"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 2)
        self.assertEqual(response_project_1["name"], project_1.name)
        self.assertEqual(response_project_2["name"], project_2.name)

    def test_all_projects_with_params(self):
        project_1 = ProjectFactory()
        ProjectFactory()
        calculate_project_fields_task()

        query = """
                query {
                    allProjects(slug: "%s") {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query % project_1.slug)
        content = json.loads(response.content)
        response_projects = content["data"]["allProjects"]["edges"]
        response_project_1 = response_projects[0]["node"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 1)
        self.assertEqual(response_project_1["name"], project_1.name)

    def test_project(self):
        site = Site.objects.first()
        city = CityFactory(site=site)
        metro_line = MetroLineFactory(city=city)
        metro = MetroFactory(line=metro_line)
        transport = TransportFactory()
        ideology = ProjectIdeologyFactory()
        ideology_cards = [ProjectIdeologyCardFactory(ideology=ideology) for _ in range(3)]
        project_1 = ProjectFactory(city=city, metro=metro, transport=transport, ideology=ideology)
        slides = [ProjectGallerySlideFactory(project=project_1) for _ in range(3)]
        advantages = [ProjectAdvantageFactory(project=project_1) for _ in range(3)]
        advantage_slides = [
            ProjectAdvantageSlideFactory(project_advantage=advantages[i]) for i in range(3)
        ]
        [FlatFactory(project=project_1) for _ in range(3)]
        furnishes = [FurnishFactory() for i in range(3)]
        [ProjectLabelFactory(projects=[project_1]) for _ in range(3)]
        furnish_images = [FurnishImageFactory(furnish=furnishes[i % 2]) for i in range(4)]
        [FurnishPointFactory(image=image) for image in furnish_images]
        project_1.furnish_set.set(furnishes)
        ProjectFactory()
        calculate_project_fields_task()

        query = """
                query { 
                    project(slug: "%s") {
                        name
                        slug
                        latitude
                        longitude
                        address
                        order
                        parkingText
                        parkingTitle
                        parkingImageDisplay
                        parkingImagePreview
                        metro {
                            name
                            line {
                                name
                            }
                        }
                        transport {
                            name
                        }
                        gallerySlides {
                            image
                            video
                            videoMobile
                        }
                        advantages {
                            title
                            advantageSlides {
                                image
                                imageDisplay
                                imageMobDisplay
                                imageLaptopDisplay
                            }
                        }
                        furnishSet {
                            id
                            imageSet {
                                id
                                pointSet {
                                    id
                                }
                            }
                        }
                        ideology {
                            id
                            ideologyCards {
                                id
                            }
                        }
                        projectLabels {
                            file
                            description
                        }
                    } 
                }
                """
        with self.assertNumQueries(9):
            response = self.query(query % project_1.slug)
        content = json.loads(response.content)
        response_project_1 = content["data"]["project"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_project_1["name"], project_1.name)
        self.assertEqual(response_project_1["slug"], project_1.slug)
        self.assertEqual(str(response_project_1["latitude"]), str(project_1.latitude))
        self.assertEqual(str(response_project_1["longitude"]), str(project_1.longitude))
        self.assertEqual(response_project_1["address"], project_1.address)
        self.assertEqual(response_project_1["order"], project_1.order)
        self.assertEqual(response_project_1["metro"]["name"], project_1.metro.name)
        self.assertEqual(response_project_1["metro"]["line"]["name"], project_1.metro.line.name)
        self.assertEqual(response_project_1["transport"]["name"], project_1.transport.name)

        self.assertEqual(len(response_project_1["gallerySlides"]), 3)
        for i in range(len(response_project_1["gallerySlides"])):
            self.assertEqual(response_project_1["gallerySlides"][i]["image"], slides[i].image.url)

        self.assertEqual(len(response_project_1["advantages"]), 3)
        for i in range(len(response_project_1["advantages"])):
            self.assertEqual(response_project_1["advantages"][i]["title"], advantages[i].title)
            for j in range(len(response_project_1["advantages"][i]["advantageSlides"])):
                self.assertEqual(
                    response_project_1["advantages"][i]["advantageSlides"][j]["image"],
                    advantage_slides[j].image.url,
                )

        self.assertEqual(len(response_project_1["furnishSet"]), 3)
        for i in range(len(response_project_1["furnishSet"])):
            self.assertEqual(int(response_project_1["furnishSet"][i]["id"]), furnishes[i].id)

        self.assertEqual(int(response_project_1["ideology"]["id"]), ideology.id)
        self.assertEqual(len(response_project_1["ideology"]["ideologyCards"]), 3)
        for i, card in enumerate(response_project_1["ideology"]["ideologyCards"]):
            self.assertEqual(int(card["id"]), ideology_cards[i].id)

        self.assertEqual(3, len(response_project_1["projectLabels"]))

    def test_project_not_active(self):
        project_1 = ProjectFactory(active=False)
        calculate_project_fields_task()

        query = """
                query { 
                    project(slug: "%s") {
                        name
                    } 
                }
                """

        with self.assertNumQueries(1):
            response = self.query(query % project_1.slug)
        response_json = response.json()
        response_project = response_json["data"]["project"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_project, None)

    def test_project_min_flat_price(self):
        for i in range(5):
            project = ProjectFactory(is_commercial=False, is_residential=True)
            [
                FlatFactory(
                    price=5000000 + 100000 * j,
                    area=50 + j,
                    project=project,
                    plan_code=j + 1 * i + 1,
                )
                for j in range(5)
            ]
            [
                FlatFactory(
                    price=5000000 + 100000 * j,
                    area=50 + j,
                    project=project,
                    plan_code=j + 1 * i + 1,
                )
                for j in range(5)
            ]
        calculate_project_fields_task()

        query = """
                query {
                    allProjects (kind: "residential") {
                        edges {
                            node {
                                minFlatPrice
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_projects = response_json["data"]["allProjects"]["edges"]

        for project in response_projects:
            self.assertEqual(project["node"]["minFlatPrice"], 5000000)

    def test_exclude(self):
        projects = [ProjectFactory() for _ in range(5)]
        calculate_project_fields_task()

        query = """
                query {
                    allProjects (exclude: "%s") {
                        edges {
                            node {
                                minFlatPrice
                            }
                        }
                    }
                }
                """

        response = self.query(query % projects[0].slug)
        response_json = response.json()
        response_projects = response_json["data"]["allProjects"]["edges"]

        self.assertEqual(len(response_projects), 4)


class AllGlobalProjectsTest(BaseTestCase):
    def test_all_global_projects(self):
        city = CityFactory()
        city_2 = CityFactory()
        project_1 = ProjectFactory(city=city)
        project_2 = ProjectFactory()
        project_3 = ProjectFactory(city=city_2)
        ProjectFactory(active=False)
        calculate_project_fields_task()

        query = """
                query {
                    allGlobalProjects {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]
        response_project_1 = response_projects[0]["node"]
        response_project_2 = response_projects[1]["node"]
        response_project_3 = response_projects[2]["node"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 3)
        self.assertEqual(response_project_1["name"], project_1.name)
        self.assertEqual(response_project_2["name"], project_2.name)
        self.assertEqual(response_project_3["name"], project_3.name)

    def test_all_global_projects_filters(self):
        city = CityFactory()
        default = [ProjectFactory(is_residential=True, is_commercial=False) for _ in range(4)]
        [ProjectFactory(is_residential=False, is_commercial=True) for _ in range(5)]
        [ProjectFactory(is_residential=True, is_commercial=False) for _ in range(6)]
        [ProjectFactory(city=city, is_residential=True, is_commercial=False) for _ in range(7)]
        calculate_project_fields_task()

        query = """
                query {
                    allGlobalProjects {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 22)

        query = """
                query {
                    allGlobalProjects (kind: "%s") {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
                """

        response = self.query(query % "commercial")
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 5)

        query = """
                   query {
                       allGlobalProjects (kind: "%s") {
                           edges {
                               node {
                                   id
                                   name
                               }
                           }
                       }
                   }
                   """

        response = self.query(query % "residential")
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 17)

        city_id = to_global_id(CityType.__name__, city.id)

        query = """
                query {
                       allGlobalProjects (city: "%s") {
                           edges {
                               node {
                                   id
                                   name
                               }
                           }
                       }
                   }
                """

        response = self.query(query % city_id)
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 7)

        query = """
                query {
                       allGlobalProjects (slug: "%s") {
                           edges {
                               node {
                                   id
                                   name
                               }
                           }
                       }
                   }
                """

        response = self.query(query % default[0].slug)
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 1)

        query = """
                query {
                       allGlobalProjects (exclude: "%s") {
                           edges {
                               node {
                                   id
                                   name
                               }
                           }
                       }
                   }
                """

        response = self.query(query % default[0].slug)
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_projects), 21)

    def test_all_global_projects_specs(self):
        [ProjectFactory() for _ in range(4)]
        [
            ProjectFactory(
                is_residential=False, is_commercial=True, status=ProjectStatusType.FUTURE
            )
            for _ in range(5)
        ]
        [
            ProjectFactory(
                is_residential=True, is_commercial=False, status=ProjectStatusType.COMPLETED
            )
            for _ in range(6)
        ]
        [ProjectFactory(city=CityFactory()) for _ in range(7)]
        calculate_project_fields_task()

        query = """
                {
                    allGlobalProjectsSpecs {
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
        response_specs = response_json["data"]["allGlobalProjectsSpecs"]

        self.assertResponseNoErrors(response)
        for spec in response_specs:
            if spec["name"] == "slug":
                self.assertEqual(len(spec["choices"]), 22)
                for i in range(len(spec["choices"])):
                    self.assertTrue(spec["choices"][i]["label"].count("Project") > 0)
                    self.assertTrue(spec["choices"][i]["value"].count("project") > 0)
            elif spec["name"] == "kind":
                self.assertEqual(len(spec["choices"]), 2)
                kind_labels = ["Коммерческие", "Жилые"]
                kind_values = ["commercial", "residential"]
                for kind in spec["choices"]:
                    self.assertTrue(kind["label"] in kind_labels)
                    self.assertTrue(kind["value"] in kind_values)
            elif spec["name"] == "city":
                self.assertEqual(len(spec["choices"]), 8)
            elif spec["name"] == "status":
                self.assertEqual(len(spec["choices"]), 3)
                status_labels = ["Текущий", "Завершенный", "Будущий"]
                status_values = ["current", "completed", "future"]
                for status in spec["choices"]:
                    self.assertTrue(status["label"] in status_labels)
                    self.assertTrue(status["value"] in status_values)

    def test_all_global_projects_facets(self):
        [ProjectFactory(active=False) for _ in range(4)]
        [
            ProjectFactory(
                is_residential=False, is_commercial=True, status=ProjectStatusType.FUTURE
            )
            for _ in range(5)
        ]
        [
            ProjectFactory(
                is_residential=True, is_commercial=False, status=ProjectStatusType.COMPLETED
            )
            for _ in range(6)
        ]
        [
            ProjectFactory(
                city=CityFactory(),
                is_residential=True,
                is_commercial=False,
                status=ProjectStatusType.CURRENT,
            )
            for _ in range(7)
        ]
        AWAITABLE_FUTURE_PROJECTS = 5
        AWAITABLE_COMPLETED_PROJECTS = 6
        AWAITABLE_CURRENT_PROJECTS = 7
        calculate_project_fields_task()

        query = """
                {
                    allGlobalProjectsFacets {
                        count
                        countCurrent
                        countFuture
                        countCompleted
                        countResidential
                        countCommercial
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
            response = self.query(query)
        response_json = response.json()
        response_facets = response_json["data"]["allGlobalProjectsFacets"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_facets["count"], 18)
        self.assertEqual(response_facets["countResidential"], 13)
        self.assertAlmostEqual(response_facets["countCommercial"], 5)
        self.assertEqual(response_facets["countCurrent"], AWAITABLE_CURRENT_PROJECTS)
        self.assertEqual(response_facets["countFuture"], AWAITABLE_FUTURE_PROJECTS)
        self.assertEqual(response_facets["countCompleted"], AWAITABLE_COMPLETED_PROJECTS)
        for facet in response_facets["facets"]:
            if facet["name"] == "slug":
                self.assertEqual(len(facet["choices"]), 18)
            elif facet["name"] == "kind":
                self.assertEqual(len(facet["choices"]), 2)
            elif facet["name"] == "city":
                self.assertEqual(len(facet["choices"]), 8)
            elif facet["name"] == "status":
                self.assertEqual(len(facet["choices"]), 3)

    def test_mortgage_annotate(self):
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
            amount=(100000, 1500000),
            deposit=(10, 50),
            rate=(10, 50),
            term=(10, 50),
            type=MortgageType.RESIDENTIAL,
        )
        offer_res.projects.add(projects[0])
        offer_res.save()
        offer_comm = OfferFactory(
            amount=(100000, 1500000),
            deposit=(10, 50),
            rate=(20, 50),
            term=(10, 50),
            type=MortgageType.COMMERCIAL,
        )
        offer_comm.projects.add(projects[0])
        offer_comm.save()
        calculate_project_fields_task()

        query = """
                query queryAllGlobalProjectsThirteen {
                    allGlobalProjects {
                        edges {
                            node {
                                slug
                                minFlatMortgage
                                minCommercialMortgage
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_projects = response_json["data"]["allGlobalProjects"]["edges"]

        self.assertResponseNoErrors(response)
        for project in response_projects:
            if project["node"]["slug"] == projects[0].slug:
                self.assertIsNotNone(project["node"]["minFlatMortgage"])
                self.assertIsNotNone(project["node"]["minCommercialMortgage"])
            else:
                self.assertIsNone(project["node"]["minFlatMortgage"])
                self.assertIsNone(project["node"]["minCommercialMortgage"])


class ProjectWebcamTestCase(BaseTestCase):
    def test_all_project_webcam(self):
        p = ProjectFactory()
        [ProjectWebcamFactory() for _ in range(3)]
        [ProjectWebcamFactory(project=p) for _ in range(3)]

        query = """
            query {
                allProjectWebcam {
                    link
                    name
                    project {
                      name
                    }
                  }
                }
            """

        with self.assertNumQueries(1):
            resp = self.query(query)

        resp_data = resp.json()
        self.assertNotIn("errors", resp_data)
        self.assertEqual(3 + 3, len(resp_data["data"]["allProjectWebcam"]))

    def test_all_project_webcam_with_slug(self):
        p = ProjectFactory()
        [ProjectWebcamFactory() for _ in range(3)]
        [ProjectWebcamFactory(project=p) for _ in range(3)]

        query = """
            query {
                allProjectWebcam(slug: "%s") {
                    link
                    name
                    project {
                      name
                    }
                  }
                }
            """

        with self.assertNumQueries(1):
            resp = self.query(query % p.slug)

        resp_data = resp.json()
        self.assertNotIn("errors", resp_data)
        self.assertEqual(3, len(resp_data["data"]["allProjectWebcam"]))

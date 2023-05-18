import json
from graphql_relay import to_global_id
from buildings.schema import BuildingType
from buildings.tests.factories import BuildingFactory
from cities.schema import CityType
from cities.tests.factories import CityFactory
from common.test_cases import BaseTestCase
from projects.schema import GlobalProjectType
from projects.tests.factories import ProjectFactory
from company.schemas.document_schema import DocumentCategoryType
from company.schemas.vacancy_schema import VacancyCategoryType
from company.tests.factories import (
    DocumentCategoryFactory,
    DocumentFactory,
    PartnersPageFactory,
    PartnersPageBlockFactory,
    VacancyFactory,
    VacancyCategoryFactory,
    VacancyPageFactory,
    VacancyPageFormFactory,
    VacancyPageAdvantageFactory,
    AboutPageFactory,
    IdeologyCardFactory,
    IdeologySliderFactory,
    LargeTenantFactory,
    PersonFactory,
    StoryFactory,
    CompanyValueFactory,
)
from ..constants import PersonCategory


class DocumentCategoryTest(BaseTestCase):
    def test_all_document_categories(self):
        categories = [DocumentCategoryFactory() for _ in range(3)]

        query = """
                query {
                    allDocumentCategories {
                        title
                        order
                    }
                }
                """
        with self.assertNumQueries(1):
            res = self.query(query)
        content = json.loads(res.content)
        res_categories = content["data"]["allDocumentCategories"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(categories), len(res_categories))
        for i, category in enumerate(categories):
            res_category = res_categories[i]
            self.assertEqual(res_category["title"], category.title)
            self.assertEqual(res_category["order"], category.order)

    def test_document_category(self):
        categories = [DocumentCategoryFactory() for _ in range(3)]
        category_id = to_global_id(DocumentCategoryType._meta.name, categories[1].id)

        query = """
                query {
                    documentCategory (id: "%s") {
                        title
                        order
                    }
                }
                """
        with self.assertNumQueries(1):
            res = self.query(query % category_id)
        content = json.loads(res.content)
        res_category = content["data"]["documentCategory"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_category["title"], categories[1].title)
        self.assertEqual(res_category["order"], categories[1].order)


class AllDocumentsTest(BaseTestCase):
    def test_default(self):
        categories = [DocumentCategoryFactory() for _ in range(3)]
        projects = [ProjectFactory() for _ in range(3)]
        documents = [
            DocumentFactory(category=categories[i % 3], project=projects[i // 3 % 3])
            for i in range(9)
        ]

        query = """
                query {
                    allDocuments {
                        edges {
                            node {
                                date
                                title
                                file
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_documents = content["data"]["allDocuments"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(documents), len(res_documents))
        for i, document in enumerate(documents):
            res_document = res_documents[i]["node"]
            self.assertEqual(res_document["date"], document.date.isoformat())
            self.assertEqual(res_document["title"], document.title)
            self.assertEqual(res_document["file"], f"/m/{document.file.name}")

    def test_filter(self):
        categories = [DocumentCategoryFactory() for _ in range(3)]
        cities = [CityFactory() for _ in range(2)]
        projects = [ProjectFactory(city=cities[i % 2]) for i in range(3)]
        documents = [
            DocumentFactory(category=categories[i % 3], project=projects[i // 3 % 3])
            for i in range(9)
        ]
        category_id = to_global_id(DocumentCategoryType._meta.name, categories[0].id)
        city_id = to_global_id(CityType._meta.name, cities[0].id)
        project_id = to_global_id(GlobalProjectType._meta.name, projects[2].id)

        query = """
                query {
                    allDocuments (category: "%s" city: "%s" project: "%s") {
                        edges {
                            node {
                                date
                                title
                                file
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query % (category_id, city_id, project_id))
        content = json.loads(res.content)
        res_documents = content["data"]["allDocuments"]["edges"]
        res_document = res_documents[0]["node"]

        self.assertResponseNoErrors(res)
        self.assertEqual(1, len(res_documents))
        self.assertEqual(res_document["date"], documents[6].date.isoformat())
        self.assertEqual(res_document["title"], documents[6].title)
        self.assertEqual(res_document["file"], f"/m/{documents[6].file.name}")

    def test_specs(self):
        categories = [DocumentCategoryFactory() for _ in range(3)]
        category_ids = [to_global_id(DocumentCategoryType.__name__, c.id) for c in categories]
        cities = [CityFactory() for _ in range(2)]
        projects = [ProjectFactory(city=cities[i % 2]) for i in range(3)]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(9)]
        [
            DocumentFactory(
                category=categories[i % 3], project=projects[i // 3 % 3], building=buildings[i]
            )
            for i in range(9)
        ]

        query = """
                query {
                    allDocumentsSpecs {
                        ... on RangeSpecType {
                            name
                            range {
                                min
                                max
                            }
                        }
                        ... on ChoiceSpecType {
                            name
                            choices {
                                value
                                label
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_specs = response_json["data"]["allDocumentsSpecs"]

        for spec in response_specs:
            if spec["name"] == "project":
                self.assertEqual(len(spec["choices"]), len(projects))
                for i in range(len(spec["choices"])):
                    self.assertEqual(spec["choices"][i]["label"], projects[i].name)
                    self.assertEqual(
                        spec["choices"][i]["value"],
                        to_global_id(GlobalProjectType.__name__, projects[i].id),
                    )
            elif spec["name"] == "city":
                self.assertEqual(len(spec["choices"]), len(cities))
                for i in range(len(spec["choices"])):
                    self.assertEqual(spec["choices"][i]["label"], cities[i].name)
                    self.assertEqual(
                        spec["choices"][i]["value"], to_global_id(CityType.__name__, cities[i].id)
                    )
            elif spec["name"] == "building":
                for i in range(len(spec["choices"])):
                    self.assertEqual(spec["choices"][i]["label"], buildings[i].name_display)
                    self.assertEqual(
                        spec["choices"][i]["value"],
                        to_global_id(BuildingType.__name__, buildings[i].id),
                    )
            elif spec["name"] == "category":
                self.assertEqual(len(spec["choices"]), len(categories))
                for i in range(len(spec["choices"])):
                    self.assertTrue(spec["choices"][i]["label"] in [c.title for c in categories])
                    self.assertTrue(spec["choices"][i]["value"] in category_ids)
            else:
                self.fail("Добавь тесты для новых спеков")

    def test_facets(self):
        categories = [DocumentCategoryFactory() for _ in range(3)]
        cities = [CityFactory() for _ in range(2)]
        projects = [ProjectFactory(city=cities[i % 2]) for i in range(3)]
        buildings = [BuildingFactory(project=projects[i % 3]) for i in range(9)]
        [
            DocumentFactory(
                category=categories[i % 3], project=projects[i // 3 % 3], building=buildings[i]
            )
            for i in range(9)
        ]
        query = """
                query {
                    allDocumentsFacets {
                        facets {
                            ... on RangeFacetType {
                                name
                                range {
                                    min
                                    max
                                }
                            }
                            ... on ChoiceFacetType {
                                name
                                choices
                            }
                        }
                    }
                }
                """

        response = self.query(query)
        response_json = response.json()
        response_facets = response_json["data"]["allDocumentsFacets"]["facets"]

        for facet in response_facets:
            if facet["name"] == "project":
                self.assertEqual(len(facet["choices"]), len(projects))
                for i in range(len(facet["choices"])):
                    self.assertEqual(
                        facet["choices"][i],
                        to_global_id(GlobalProjectType.__name__, projects[i].id),
                    )
            elif facet["name"] == "city":
                self.assertEqual(len(facet["choices"]), len(cities))
                for i in range(len(facet["choices"])):
                    self.assertEqual(
                        facet["choices"][i], to_global_id(CityType.__name__, cities[i].id)
                    )

            elif facet["name"] == "building":
                for i in range(len(facet["choices"])):
                    self.assertEqual(
                        facet["choices"][i], to_global_id(BuildingType.__name__, buildings[i].id)
                    )
            elif facet["name"] == "category":
                for i in range(len(facet["choices"])):
                    self.assertEqual(
                        facet["choices"][i],
                        to_global_id(DocumentCategoryType.__name__, categories[i].id),
                    )
            elif facet["name"] == "is_investors":
                self.assertSetEqual(set(facet["choices"]), {"false"})
            else:
                self.fail("Добавь тесты для новых фасетов")


class PartnersPageTest(BaseTestCase):
    def test_default(self):
        page = PartnersPageFactory()
        blocks = [PartnersPageBlockFactory(page=page) for _ in range(3)]

        query = """
                query {
                    partnersPage {
                        text1
                        partnerspageblockSet {
                            title
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_page = content["data"]["partnersPage"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_page["text1"], page.text_1)
        for i, res_advantage in enumerate(res_page["partnerspageblockSet"]):
            self.assertEqual(res_advantage["title"], blocks[i].title)


class AllVacanciesTest(BaseTestCase):
    def test_default(self):
        city = CityFactory()
        categories = [VacancyCategoryFactory() for _ in range(3)]
        vacancies = [VacancyFactory(category=categories[i], city=city) for i in range(3)]
        not_active_city = CityFactory(active=False)
        [VacancyFactory(city=not_active_city, category=categories[i]) for i in range(2)]

        query = """
                query {
                    allVacancies {
                        edges {
                            node {
                                jobTitle
                                category {
                                    name
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_vacancies = content["data"]["allVacancies"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_vacancies), len(vacancies))
        for i, res_vacancy in enumerate(res_vacancies):
            self.assertEqual(res_vacancy["node"]["jobTitle"], vacancies[i].job_title)
            self.assertEqual(res_vacancy["node"]["category"]["name"], vacancies[i].category.name)

    def test_filter(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [VacancyCategoryFactory() for _ in range(2)]
        vacancies = [
            VacancyFactory(city=cities[i % 2], category=categories[i // 2]) for i in range(4)
        ]

        city_id = to_global_id(CityType.__name__, cities[0].id)
        category_id = to_global_id(VacancyCategoryType.__name__, categories[0].id)
        text = vacancies[0].job_title

        query = """
                query {
                    allVacancies (city: "%s" category: "%s" text: "%s") {
                        edges {
                            node {
                                jobTitle
                                city {
                                    id
                                }
                                category {
                                    id
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query % (city_id, category_id, text))
        content = json.loads(res.content)
        res_vacancies = content["data"]["allVacancies"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_vacancies), 1)
        self.assertEqual(res_vacancies[0]["node"]["jobTitle"], vacancies[0].job_title)


class AllVacanciesFacetsTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [VacancyCategoryFactory() for _ in range(2)]
        [VacancyFactory(city=cities[i], category=categories[i]) for i in range(2)]
        not_active_cities = [CityFactory(active=False) for _ in range(2)]
        [VacancyFactory(city=not_active_cities[i], category=categories[i]) for i in range(2)]

        query = """
                query {
                    allVacanciesFacets {
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
        res_facets = content["data"]["allVacanciesFacets"]["facets"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_facets), 2)
        self.assertEqual(res_facets[0]["name"], "city")
        self.assertTrue(to_global_id(CityType.__name__, cities[0].id) in res_facets[0]["choices"])
        self.assertTrue(to_global_id(CityType.__name__, cities[0].id) in res_facets[0]["choices"])
        self.assertEqual(res_facets[1]["name"], "category")
        for i, category_id in enumerate(res_facets[1]["choices"][::-1]):
            self.assertEqual(
                category_id, to_global_id(VacancyCategoryType.__name__, categories[i].id)
            )


class AllVacanciesSpecsTest(BaseTestCase):
    def test_default(self):
        cities = [CityFactory() for _ in range(2)]
        categories = [VacancyCategoryFactory() for _ in range(2)]
        [VacancyFactory(city=cities[i], category=categories[i]) for i in range(2)]
        not_active_cities = [CityFactory(active=False) for _ in range(2)]
        [VacancyFactory(city=not_active_cities[i], category=categories[i]) for i in range(2)]

        query = """
                query {
                    allVacanciesSpecs {
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

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        res_facets = content["data"]["allVacanciesSpecs"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_facets), 2)
        self.assertEqual(res_facets[0]["name"], "city")
        for i, city in enumerate(res_facets[0]["choices"]):
            self.assertEqual(city["label"], cities[i].name)
            self.assertEqual(city["value"], to_global_id(CityType.__name__, cities[i].id))
        self.assertEqual(res_facets[1]["name"], "category")
        for i, category in enumerate(res_facets[1]["choices"]):
            self.assertEqual(category["label"], categories[i].name)
            self.assertEqual(
                category["value"], to_global_id(VacancyCategoryType.__name__, categories[i].id)
            )


class VacancyPageTest(BaseTestCase):
    def test_default(self):
        form = VacancyPageFormFactory()
        page = VacancyPageFactory(form=form)
        advantages = [VacancyPageAdvantageFactory(page=page) for _ in range(3)]

        query = """
                 query {
                    vacancyPage {
                        text1
                        vacancypageadvantageSet {
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
        res_page = content["data"]["vacancyPage"]

        self.assertResponseNoErrors(res)
        self.assertEqual(res_page["text1"], page.text_1)
        for i, res_advantage in enumerate(res_page["vacancypageadvantageSet"]):
            self.assertEqual(res_advantage["title"], advantages[i].title)
        self.assertEqual(res_page["form"]["title"], form.title)


class AboutPageTest(BaseTestCase):
    def setUp(self):
        about = AboutPageFactory()
        [IdeologyCardFactory(about_section=about) for _ in range(5)]
        [IdeologySliderFactory(about_section=about) for _ in range(7)]
        [LargeTenantFactory(about_section=about) for _ in range(4)]
        [StoryFactory(about_section=about) for _ in range(4)]
        [CompanyValueFactory(about_section=about) for _ in range(4)]

    def test_about_section(self):
        query = """
                query {
                    aboutPage {
                        text1
                        text2
                        offices
                        description
                        image
                        imageDisplay
                        imagePreview
                        ideologyDescription
                        ideologyText
                        ideologyImageOne
                        ideologyImageOneDisplay
                        ideologyImageOnePreview
                        ideologycardSet {
                            title
                            text
                            image
                            order
                            imageDisplay
                            imagePreview
                        }
                        ideologysliderSet {
                            text
                            order
                        }
                        largetenantSet {
                            name
                        }
                        storySet {
                            name
                            fileDisplay
                            filePreview
                            images {
                                text
                                fileDisplay
                                filePreview
                            }
                        }
                        companyvalueSet {
                            name
                            text
                            fileDisplay
                            filePreview
                        }
                    }
                }
                """

        response = self.query(query)
        self.assertResponseNoErrors(response)

        response_json = response.json()
        response_data = response_json["data"]
        response_page = response_data["aboutPage"]
        response_cards = response_page["ideologycardSet"]
        response_sliders = response_page["ideologysliderSet"]
        response_stories = response_page["storySet"]
        response_company_values = response_page["companyvalueSet"]

        AWAITABLE_STATUS = 200
        AWAITABLE_SECTION_LEN = 17
        AWAITABLE_CARDS_LEN = 5
        AWAITABLE_SLIDERS_LEN = 7
        AWAITABLE_CARD_LEN = 6
        AWAITABLE_SLIDER_LEN = 2
        AWAITABLE_STORIES_LEN = 4
        AWAITABLE_VALUES_LEN = 4

        self.assertEqual(response.status_code, AWAITABLE_STATUS)
        self.assertEqual(len(response_page), AWAITABLE_SECTION_LEN)
        self.assertEqual(len(response_cards), AWAITABLE_CARDS_LEN)
        self.assertEqual(len(response_sliders), AWAITABLE_SLIDERS_LEN)
        self.assertEqual(len(response_stories), AWAITABLE_STORIES_LEN)
        self.assertEqual(len(response_company_values), AWAITABLE_VALUES_LEN)

        for value in response_page.values():
            self.assertIsNotNone(value)

        for card in response_cards:
            self.assertEqual(len(card), AWAITABLE_CARD_LEN)
            for value in card.values():
                self.assertIsNotNone(value)

        for slider in response_sliders:
            self.assertEqual(len(slider), AWAITABLE_SLIDER_LEN)
            for value in slider.items():
                self.assertIsNotNone(value)

    def test_all_person(self):
        [PersonFactory(category=PersonCategory.MANAGER) for _ in range(3)]
        [PersonFactory(category=PersonCategory.DIRECTOR) for _ in range(2)]

        query = """
            query {
              allPersons (category: "%s") {
                firstName
                lastName
                bio
              }
            }
        """

        with self.assertNumQueries(1):
            resp = self.query(query % PersonCategory.MANAGER)

        self.assertResponseNoErrors(resp)
        person_data = resp.json()["data"]["allPersons"]
        self.assertEqual(3, len(person_data))

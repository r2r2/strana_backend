import json
from datetime import timedelta
from django.contrib.sites.models import Site
from django.utils.timezone import now
from graphql_relay import to_global_id
from cities.schema import CityType
from cities.tests.factories import SiteFactory, CityFactory
from common.test_cases import BaseTestCase
from projects.tests.factories import ProjectFactory
from projects.schema import ProjectType
from ..constants import NewsType
from .factories import NewsFactory, NewsSlideFactory, MassMediaFactory, NewsFormFactory


class TestNews(BaseTestCase):
    def test_all_news(self):
        news = [
            NewsFactory(),
            NewsFactory(start=now() - timedelta(days=2)),
            NewsFactory(start=now() - timedelta(days=1)),
        ]
        image = NewsSlideFactory(news=news[0], video="")
        video = NewsSlideFactory(news=news[1], image="")
        NewsFactory(published=False)
        NewsFactory(start=now() + timedelta(days=1))
        NewsFactory(end=now() - timedelta(days=1))

        query = """
                query {
                    allNews (order: "-start"){
                        edges {
                            node {
                                id
                                title
                                imageSlideSet {
                                    id
                                    title
                                }
                                videoSlideSet {
                                    id
                                    title
                                }
                                form {
                                  title
                                  yandexMetrics
                                  googleEventName
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(5):
            response = self.query(query)
        content = json.loads(response.content)
        response_news = content["data"]["allNews"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_news), len(news))
        self.assertEqual(response_news[0]["node"]["title"], news[0].title)
        self.assertEqual(response_news[0]["node"]["imageSlideSet"][0]["title"], image.title)
        self.assertEqual(response_news[1]["node"]["title"], news[2].title)
        self.assertEqual(response_news[2]["node"]["title"], news[1].title)
        self.assertEqual(response_news[2]["node"]["videoSlideSet"][0]["title"], video.title)

    def test_news(self):
        NewsFactory()
        news = NewsFactory(type=NewsType.NEWS)
        NewsFactory()

        query = """
                query {
                news(slug: "%s") {
                    id
                    title
                    intro
                }
            }
                """
        response = self.query(query % news.slug)
        content = json.loads(response.content)
        response_news_1 = content["data"]["news"]

        self.assertResponseNoErrors(response)
        self.assertEqual(response_news_1["title"], news.title)

    def test_news_with_another_news(self):
        another_news = [
            NewsFactory(type=NewsType.NEWS, start=now() - timedelta(days=i)) for i in range(2)
        ]
        news = NewsFactory(type=NewsType.NEWS)

        query = """
                query {
                    news(slug: "%s") {
                        id
                        title
                        intro
                        anotherNews(limit: 2) {
                            id
                            title
                            intro
                        }
                    }
                }
                """
        with self.assertNumQueries(4):
            res = self.query(query % news.slug)
        content = json.loads(res.content)
        res_another_news = content["data"]["news"]["anotherNews"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_another_news), 2)
        for i, res_news in enumerate(res_another_news):
            self.assertEqual(res_news["title"], another_news[i].title)

    def test_news_by_project(self):
        project_1 = ProjectFactory()
        project_2 = ProjectFactory()
        news_1 = NewsFactory(start=now() - timedelta(days=1))
        news_2 = NewsFactory(start=now() - timedelta(days=2))
        news_3 = NewsFactory(start=now() - timedelta(days=3))
        NewsFactory()
        news_1.projects.add(project_1)
        news_2.projects.add(project_2)
        news_3.projects.add(project_1)
        news_3.projects.add(project_2)

        query = """
                query {
                project(slug: "%s") {
                    newsSet {
                        edges {
                            node {
                                title
                            }
                        }
                    }
                }
            }
                """

        response = self.query(query % project_1.slug)
        content = json.loads(response.content)
        response_news = content["data"]["project"]["newsSet"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_news), 2)
        self.assertEqual(response_news[0]["node"]["title"], news_1.title)
        self.assertEqual(response_news[1]["node"]["title"], news_3.title)

    def test_with_filters(self):
        project_1 = ProjectFactory()
        project_2 = ProjectFactory()
        news_1 = NewsFactory(type=NewsType.NEWS, start=now() - timedelta(days=1))
        news_2 = NewsFactory(type=NewsType.ACTION, start=now() - timedelta(days=2))
        news_3 = NewsFactory(type=NewsType.PROGRESS, start=now() - timedelta(days=3))
        NewsSlideFactory(news=news_3, video="")
        news_4 = NewsFactory(type=NewsType.VIDEO, start=now() - timedelta(days=4))
        news_1.projects.add(project_1)
        news_2.projects.add(project_2)
        news_3.projects.add(project_1)
        news_4.projects.add(project_2)

        query = """
                query {
                    allNews (project: "%s", type: "%s") {
                        edges {
                            node {
                                title
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(
                query % (to_global_id(ProjectType.__name__, project_1.slug), NewsType.PROGRESS)
            )
        content = json.loads(res.content)
        response_news = content["data"]["allNews"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(response_news), 1)
        self.assertEqual(response_news[0]["node"]["title"], news_3.title)

    def test_filter_projects_kind(self):
        site = Site.objects.get(domain="example.com")
        city = CityFactory(site=site)
        project_1 = ProjectFactory(is_residential=True, is_commercial=False, city=city)
        project_2 = ProjectFactory(is_residential=False, is_commercial=True, city=city)

        for _ in range(5):
            news_one = NewsFactory()
            news_two = NewsFactory()
            news_one.projects.add(project_1)
            news_two.projects.add(project_2)
            news_one.save()
            news_two.save()

        query = """
                query {
                    allNews (projectsKind: "%s"){
                        edges {
                            node {
                                title
                            }
                        }
                    }
                }
                """

        response = self.query(query % "commercial")
        response_json = response.json()

        response_news = response_json["data"]["allNews"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_news), 5)

    def test_filter_projects_city(self):
        site_1 = Site.objects.get(domain="example.com")
        city_1 = CityFactory(site=site_1)
        site_2 = SiteFactory()
        city_2 = CityFactory(site=site_2)
        project_1 = ProjectFactory(is_residential=True, is_commercial=False, city=city_1)
        project_2 = ProjectFactory(is_residential=False, is_commercial=True, city=city_1)

        for _ in range(5):
            news_one = NewsFactory()
            news_two = NewsFactory()
            news_one.projects.add(project_1)
            news_two.projects.add(project_2)
            news_one.save()
            news_two.save()

        city_1_id = to_global_id(CityType.__name__, city_1.id)
        city_2_id = to_global_id(CityType.__name__, city_2.id)

        query = """
                query {
                    allNews (projectsCity: "%s"){
                        edges {
                            node {
                                title
                            }
                        }
                    }
                }
                """
        response = self.query(query % city_1_id)
        response_json = response.json()
        response_news = response_json["data"]["allNews"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_news), 10)

        response = self.query(query % city_2_id)
        response_json = response.json()
        response_news = response_json["data"]["allNews"]["edges"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(response_news), 0)

    def test_about_us_type(self):
        mm = MassMediaFactory()
        n = NewsFactory(type=NewsType.ABOUT_US, mass_media=mm, source_link="example.com")
        [NewsFactory() for _ in range(3)]

        query = """
                query {
                    allNews (type: "%s"){
                        edges {
                            node {
                                title
                                type
                                sourceLink
                                massMedia {
                                  name
                                  logo
                                }
                            }
                        }
                    }
                }
                """
        response = self.query(query % NewsType.ABOUT_US)
        self.assertResponseNoErrors(response)

        data = response.json()["data"]["allNews"]["edges"]
        self.assertEqual(1, len(data))

        news_data = data[0]["node"]

        self.assertEqual(news_data["title"], n.title)
        self.assertEqual(news_data["sourceLink"], n.source_link)
        self.assertIsNotNone(news_data["massMedia"])
        self.assertEqual(news_data["massMedia"]["name"], mm.name)
        self.assertIsNotNone(news_data["massMedia"]["logo"])


class AllNewsFacetsTest(BaseTestCase):
    def test_default(self):
        site_1 = Site.objects.get(domain="example.com")
        city_1 = CityFactory(site=site_1)
        site_2 = SiteFactory()
        city_2 = CityFactory(site=site_2)
        cities_ids = [
            to_global_id(CityType.__name__, city_1.id),
            to_global_id(CityType.__name__, city_2.id),
        ]
        project_1 = ProjectFactory(is_residential=True, is_commercial=False, city=city_1)
        project_2 = ProjectFactory(is_residential=False, is_commercial=True, city=city_2)
        news_1 = [
            NewsFactory(type=NewsType.NEWS, start=now() - timedelta(days=1)) for _ in range(2)
        ]
        news_2 = [
            NewsFactory(type=NewsType.ACTION, start=now() - timedelta(days=2)) for _ in range(2)
        ]
        news_3 = [
            NewsFactory(type=NewsType.PROGRESS, start=now() - timedelta(days=3)) for _ in range(2)
        ]
        [NewsSlideFactory(news=news, video="") for news in news_3]
        news_4 = [
            NewsFactory(type=NewsType.VIDEO, start=now() - timedelta(days=4)) for _ in range(2)
        ]
        news_5 = [
            NewsFactory(type=NewsType.STREAM, start=now() - timedelta(days=4)) for _ in range(2)
        ]
        news_6 = [
            NewsFactory(type=NewsType.ABOUT_US, start=now() - timedelta(days=4)) for _ in range(2)
        ]
        news_7 = [
            NewsFactory(type=NewsType.ACTION_LANDING, start=now() - timedelta(days=4))
            for _ in range(2)
        ]

        [news.projects.add(project_1) for news in news_1]
        [news.projects.add(project_2) for news in news_2]
        [news.projects.add(project_1) for news in news_3]
        [news.projects.add(project_2) for news in news_4]
        [news.projects.add(project_1) for news in news_5]
        [news.projects.add(project_1) for news in news_6]
        [news.projects.add(project_1) for news in news_7]

        query = """
                query {
                    allNewsFacets {
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
        with self.assertNumQueries(6):
            res = self.query(query)
        content = json.loads(res.content)
        res_facets = content["data"]["allNewsFacets"]["facets"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_facets), 4)
        self.assertEqual(res_facets[0]["name"], "project")
        self.assertEqual(len(res_facets[0]["choices"]), 2)
        self.assertSetEqual(
            set(res_facets[0]["choices"]),
            set(
                [
                    to_global_id(ProjectType.__name__, project.slug)
                    for project in [project_1, project_2]
                ]
            ),
        )
        self.assertEqual(res_facets[1]["name"], "type")
        self.assertEqual(len(res_facets[1]["choices"]), 7)
        self.assertSetEqual(set(res_facets[1]["choices"]), {type[0] for type in NewsType.choices})
        self.assertEqual(res_facets[2]["name"], "projectsKind")
        self.assertEqual(len(res_facets[2]["choices"]), 2)
        self.assertEqual(res_facets[3]["name"], "projectsCity")
        for choice in res_facets[3]["choices"]:
            self.assertTrue(choice in cities_ids)


class AllNewsSpecsTest(BaseTestCase):
    def test_default(self):
        site_1 = Site.objects.get(domain="example.com")
        city_1 = CityFactory(site=site_1)
        site_2 = SiteFactory()
        city_2 = CityFactory(site=site_2)
        cities_ids = [
            to_global_id(CityType.__name__, city_1.id),
            to_global_id(CityType.__name__, city_2.id),
        ]
        cities_names = [city_1.name, city_2.name]
        project_1 = ProjectFactory(is_residential=True, is_commercial=False, city=city_1)
        project_2 = ProjectFactory(is_residential=False, is_commercial=True, city=city_2)
        news_1 = [
            NewsFactory(type=NewsType.NEWS, start=now() - timedelta(days=1)) for _ in range(2)
        ]
        news_2 = [
            NewsFactory(type=NewsType.ACTION, start=now() - timedelta(days=2)) for _ in range(2)
        ]
        news_3 = [
            NewsFactory(type=NewsType.PROGRESS, start=now() - timedelta(days=3)) for _ in range(2)
        ]
        [NewsSlideFactory(news=news, video="") for news in news_3]
        news_4 = [
            NewsFactory(type=NewsType.VIDEO, start=now() - timedelta(days=4)) for _ in range(2)
        ]
        news_5 = [
            NewsFactory(type=NewsType.STREAM, start=now() - timedelta(days=4)) for _ in range(2)
        ]
        news_6 = [
            NewsFactory(type=NewsType.ABOUT_US, start=now() - timedelta(days=4)) for _ in range(2)
        ]
        news_7 = [
            NewsFactory(type=NewsType.ACTION_LANDING, start=now() - timedelta(days=4))
            for _ in range(2)
        ]
        [news.projects.add(project_1) for news in news_1]
        [news.projects.add(project_2) for news in news_2]
        [news.projects.add(project_1) for news in news_3]
        [news.projects.add(project_2) for news in news_4]
        [news.projects.add(project_1) for news in news_5]
        [news.projects.add(project_1) for news in news_6]
        [news.projects.add(project_1) for news in news_7]

        query = """
                query {
                    allNewsSpecs {
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

        with self.assertNumQueries(5):
            res = self.query(query)
        content = json.loads(res.content)
        res_specs = content["data"]["allNewsSpecs"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_specs), 4)
        self.assertEqual(res_specs[0]["name"], "project")
        self.assertEqual(len(res_specs[0]["choices"]), 2)
        self.assertEqual(
            res_specs[0]["choices"][0]["value"], to_global_id(ProjectType.__name__, project_1.slug)
        )
        self.assertEqual(res_specs[0]["choices"][0]["label"], project_1.name)
        self.assertEqual(
            res_specs[0]["choices"][1]["value"], to_global_id(ProjectType.__name__, project_2.slug)
        )
        self.assertEqual(res_specs[0]["choices"][1]["label"], project_2.name)
        self.assertEqual(res_specs[1]["name"], "type")
        self.assertEqual(len(res_specs[1]["choices"]), 7)
        for i, (value, label) in enumerate(sorted(NewsType.choices)):
            self.assertEqual(res_specs[1]["choices"][i]["value"], value)
            self.assertEqual(res_specs[1]["choices"][i]["label"], label)
        self.assertEqual(res_specs[2]["name"], "projectsKind")
        self.assertEqual(res_specs[3]["name"], "projectsCity")
        for choice in res_specs[3]["choices"]:
            self.assertTrue(choice["value"] in cities_ids)
            self.assertTrue(choice["label"] in cities_names)


class AllProgressTest(BaseTestCase):
    def test_default(self):
        NewsFactory(type=NewsType.NEWS, start=now() - timedelta(days=1))
        NewsFactory(type=NewsType.ACTION, start=now() - timedelta(days=2))
        progress = [
            NewsFactory(
                type=NewsType.PROGRESS, start=now() - timedelta(days=3 + i % 3), date=now().date()
            )
            for i in range(3)
        ]
        NewsFactory(type=NewsType.VIDEO, start=now() - timedelta(days=6))
        [
            NewsSlideFactory(news=progress[i % 3], image="")
            if i % 2
            else NewsSlideFactory(news=progress[i % 3], video="")
            for i in range(18)
        ]
        NewsFactory(type=NewsType.PROGRESS, start=now() + timedelta(days=1), published=False)
        NewsFactory(
            type=NewsType.PROGRESS,
            start=now() - timedelta(days=10),
            end=now() - timedelta(days=5),
            published=False,
        )

        query = """
                query {
                    allProgress {
                        edges {
                            node {
                                slug
                                slideSet {
                                    id
                                    title
                                }
                            }
                        }
                    }
                }
                """
        with self.assertNumQueries(4):
            res = self.query(query)
        content = json.loads(res.content)
        res_progress = content["data"]["allProgress"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_progress), len(progress))
        for i, _progress in enumerate(res_progress):
            self.assertEqual(_progress["node"]["slug"], progress[i].slug)

        query = """
                query {
                    allProgress {
                        edges {
                            node {
                                slug
                                slideSetCount
                                slideSet (first:1) {
                                    id
                                    title
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(4):
            res = self.query(query)
        content = json.loads(res.content)
        res_progress = content["data"]["allProgress"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_progress), 3)
        for i, _progress in enumerate(res_progress):
            self.assertEqual(_progress["node"]["slug"], progress[i].slug)
            self.assertEqual(len(_progress["node"]["slideSet"]), 1)
            self.assertIsNotNone(_progress["node"]["slideSetCount"])

    def test_with_params(self):
        quarters = {
            1: "I",
            2: "I",
            3: "I",
            4: "II",
            5: "II",
            6: "II",
            7: "III",
            8: "III",
            9: "III",
            10: "IV",
            11: "IV",
            12: "IV",
        }
        projects = [ProjectFactory() for _ in range(2)]

        NewsFactory(type=NewsType.NEWS, start=now() - timedelta(days=1))
        NewsFactory(type=NewsType.ACTION, start=now() - timedelta(days=2))
        NewsFactory(type=NewsType.VIDEO, start=now() - timedelta(days=5))

        progress = [
            NewsFactory(
                type=NewsType.PROGRESS,
                start=now() - timedelta(days=1),
                date=(now() - timedelta(days=i * 367)).date(),
            )
            for i in range(4)
        ]

        for i in range(4):
            progress[i].projects.add(projects[i % 2])

        query = """
                 query {
                    allProgress (project: "%s", date: "%s") {
                        edges {
                            node {
                                slug
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(3):
            res = self.query(
                query
                % (
                    to_global_id(ProjectType.__name__, projects[0].slug),
                    f"{quarters[progress[2].date.month]}-{progress[2].date.year}",
                )
            )
        content = json.loads(res.content)
        res_progress = content["data"]["allProgress"]["edges"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_progress), 1)
        self.assertEqual(res_progress[0]["node"]["slug"], progress[2].slug)


#
# class TestAllProgressSpecs(BaseTestCase):
#     def test_default(self):
#         projects = [ProjectFactory() for _ in range(2)]
#         progress = [
#             NewsFactory(type=NewsType.PROGRESS, date=(now() - timedelta(days=i * 31)).date(),)
#             for i in range(4)
#         ]
#
#         for i in range(4):
#             progress[i].projects.add(projects[i % 2])
#
#         query = """
#                 query {
#                     allProgressSpecs {
#                         ...on RangeSpecType {
#                             name
#                             range {
#                                 min
#                                 max
#                             }
#                         }
#                         ...on ChoiceSpecType {
#                             name
#                             choices {
#                                 value
#                                 label
#                             }
#                         }
#                     }
#                 }
#                 """
#         with self.assertNumQueries(2):
#             res = self.query(query)
#         content = json.loads(res.content)
#         res_specs = content["data"]["allProgressSpecs"]
#
#         self.assertResponseNoErrors(res)
#         self.assertEqual(len(res_specs), 2)
#         self.assertEqual(res_specs[0]["name"], "project")
#         for i, project in enumerate(projects):
#             self.assertEqual(
#                 res_specs[0]["choices"][i]["value"],
#                 to_global_id(ProjectType.__name__, project.slug),
#             )
#             self.assertEqual(res_specs[0]["choices"][i]["label"], project.name)
#         self.assertEqual(res_specs[1]["name"], "date")
#         self.assertEqual(len(res_specs[1]["choices"]), 2)


class TestAllProgressFacets(BaseTestCase):
    def test_default(self):
        quarters = {
            1: "I",
            2: "I",
            3: "I",
            4: "II",
            5: "II",
            6: "II",
            7: "III",
            8: "III",
            9: "III",
            10: "IV",
            11: "IV",
            12: "IV",
        }
        projects = [ProjectFactory() for _ in range(2)]
        progress = [
            NewsFactory(type=NewsType.PROGRESS, date=(now() - timedelta(days=i * 31)).date())
            for i in range(4)
        ]
        for i in range(4):
            progress[i].projects.add(projects[i % 2])

        query = """
                query {
                    allProgressFacets {
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
        res_facets = content["data"]["allProgressFacets"]["facets"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(res_facets), 2)
        self.assertEqual(res_facets[0]["name"], "project")
        self.assertSetEqual(
            set(res_facets[0]["choices"]),
            set([to_global_id(ProjectType.__name__, project.slug) for project in projects]),
        )
        self.assertEqual(res_facets[1]["name"], "date")
        self.assertSetEqual(
            set(res_facets[1]["choices"]),
            set([f"{quarters[pg.date.month]}-{pg.date.year}" for pg in progress]),
        )

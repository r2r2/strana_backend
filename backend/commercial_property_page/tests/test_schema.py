import json
from datetime import timedelta
from django.contrib.sites.models import Site
from django.utils.timezone import now
from graphql_relay import to_global_id
from .factories import (
    CommercialPropertyPageAdvantageFactory,
    CommercialPropertyPageFactory,
    CommercialPropertyPageSlideFactory,
)
from common.test_cases import BaseTestCase
from cities.schema import CityType
from cities.tests.factories import CityFactory, SiteFactory
from projects.tests.factories import ProjectFactory
from properties.tests.factories import (
    CommercialPremiseFactory,
    FurnishImageFactory,
    FurnishPointFactory,
    FurnishFactory,
)


class CommercialPropertyPageTest(BaseTestCase):
    def test_page(self):
        site = Site.objects.first()
        city = CityFactory(site=site)
        page = CommercialPropertyPageFactory(city=city)
        advantages = [CommercialPropertyPageAdvantageFactory(page=page) for i in range(2)]
        slides = [CommercialPropertyPageSlideFactory(page=page) for i in range(2)]
        projects = [ProjectFactory(city=city) for i in range(2)]
        properties = [
            CommercialPremiseFactory(
                project=projects[i % 2],
                price=10000 + 10000 * i,
                area=10 + 10 * i,
                promo_start=now() - timedelta(days=2 - i),
            )
            for i in range(4)
        ]
        furnishes = [FurnishFactory() for i in range(4)]
        furnish_images = [FurnishImageFactory(furnish=furnishes[i % 2]) for i in range(4)]
        [FurnishPointFactory(image=image) for image in furnish_images]
        for i, furnish in enumerate(furnishes):
            page.furnish_set.add(furnish)
            properties[i].furnish_set.add(furnish)

        query = """
                {
                    commercialPropertyPage (city: "%s") {
                        minPrice
                        areaRange {
                            min
                            max
                        }
                        city {
                            id
                            name
                        }
                        slideSet {
                            id
                            order
                            imagePreview
                            imageDisplay
                        }
                        advantageSet {
                            id
                            title
                        }
                        furnishSet {
                             id
                            name
                            imageSet {
                                id
                                fileDisplay
                                filePreview
                                pointSet {
                                    point
                                    text
                                }
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(6):
            res = self.query(query % to_global_id(CityType.__name__, city.id))
        content = json.loads(res.content)
        page = content["data"]["commercialPropertyPage"]

        self.assertResponseNoErrors(res)
        self.assertEqual(page["minPrice"], properties[0].price)
        self.assertEqual(page["areaRange"], {"min": properties[0].area, "max": properties[-1].area})
        self.assertEqual(page["city"]["name"], city.name)
        self.assertEqual(len(page["slideSet"]), 2)
        for i, slide in enumerate(page["slideSet"]):
            self.assertEqual(int(slide["id"]), slides[i].id)
        self.assertEqual(len(page["advantageSet"]), 2)
        for i, advantage in enumerate(page["advantageSet"]):
            self.assertEqual(int(advantage["id"]), advantages[i].id)
        self.assertEqual(len(page["furnishSet"]), 4)
        for i, res_furnish in enumerate(page["furnishSet"]):
            self.assertEqual(int(res_furnish["id"]), furnishes[i].id)


class TestCommercialPropertyPageSpecs(BaseTestCase):
    def test_default(self):
        sites = [SiteFactory() for _ in range(3)]
        cities = [CityFactory(site=sites[i]) for i in range(3)]
        [CommercialPropertyPageFactory(city=cities[i]) for i in range(3)]

        query = """
                {
                    commercialPropertyPageSpecs {
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
        with self.assertNumQueries(1):
            res = self.query(query)

        content = json.loads(res.content)
        specs = content["data"]["commercialPropertyPageSpecs"]

        self.assertResponseNoErrors(res)
        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0]["name"], "city")
        for i, city in enumerate(specs[0]["choices"]):
            self.assertEqual(city["value"], to_global_id(CityType.__name__, cities[i].id))
            self.assertEqual(city["label"], cities[i].name)

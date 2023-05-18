from graphql_relay import to_global_id

from news.constants import NewsType
from news.tests.factories import NewsFactory
from common.test_cases import BaseTestCase
from projects.tests.factories import ProjectFactory
from properties.tests.factories import FurnishFactory

from .factories import (
    LandingFactory,
    LandingBlockFactory,
    SliderBlockSlideFactory,
    StepsBlockItemFactory,
    ListBlockItemFactory,
    DigitsBlockItemFactory,
    AdvantageBlockItemFactory,
    TwoColumnsBlockItemFactory,
)
from ..schema import LandingBlockType
from ..constants import LandingBlockChoices


class LandingTest(BaseTestCase):
    def test_landing(self):
        landing = LandingFactory()
        blocks = [LandingBlockFactory(landing=landing) for _ in range(7)]
        block_ids = [to_global_id(LandingBlockType.__name__, b.id) for b in blocks]

        query = """
            query {
              landing (slug: "%s") {
                slug
                bars
                blockIds
              }
            }
        """

        with self.assertNumQueries(3):
            resp = self.query(query % landing.slug)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]["landing"]

        self.assertEqual(landing.slug, resp_data["slug"])
        self.assertSetEqual(set(block_ids), set(resp_data["blockIds"]))

    def test_all_landings(self):
        for i in range(5):
            landing = LandingFactory()
            furnishes = [FurnishFactory() for _ in range(3)]
            progress_set = [NewsFactory(type=NewsType.PROGRESS) for _ in range(3)]
            projects = [ProjectFactory() for _ in range(3)]
            blocks = [
                LandingBlockFactory(
                    landing=landing,
                    project=projects[i % 3],
                    furnishes=furnishes,
                    progress_set=progress_set,
                )
                for i in range(3)
            ]
            for block in blocks:
                [SliderBlockSlideFactory(block=block) for _ in range(2)]
                [StepsBlockItemFactory(block=block) for _ in range(2)]
                [DigitsBlockItemFactory(block=block) for _ in range(2)]
                [AdvantageBlockItemFactory(block=block) for _ in range(2)]
                [TwoColumnsBlockItemFactory(block=block) for _ in range(2)]
                [ListBlockItemFactory(block=block) for _ in range(2)]

        query = """
        query {
                allLandings {
                    slug
                    title
                    end
                    text
                    isPromo
                    metaTitle
                    metaKeywords
                    metaDescription
                    mainImageDisplay
                    mainImagePreview
                    cardImageDisplay
                    cardImagePreview
                    landingblockSet {
                        title
                        text
                        order
                        anchor
                        blockType
                        ctaBlockType
                        image1Display
                        image1Preview
                        image1Description
                        image2Display
                        image2Preview
                        image2Description
                        image3Display
                        image3Preview
                        isFullScreen
                        buttonName1
                        buttonLink1
                        buttonName2
                        buttonLink2
                        slides {
                            fileDisplay
                            filePreview
                        }
                        twoColumnItems {
                            fileDisplay
                            filePreview
                            subtitle
                            description
                        }
                        furnishes {
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
                        digitItems {
                            title
                            subtitle
                            text
                        }
                        advantages {
                            fileDisplay
                            filePreview
                            subtitle
                            description
                        }
                        steps {
                            title
                            text
                        }
                        progressSet {
                            title
                        }
                        newsSet {
                            title
                        }
                        listItems {
                            title
                        }
                        flatSet {
                            id
                        }
                    }
                }
            }
        """

        with self.assertNumQueries(13):
            resp = self.query(query)
        self.assertResponseNoErrors(resp)

        data = resp.json()["data"]["allLandings"]

        self.assertEqual(5, len(data))
        for landing in data:
            self.assertEqual(3, len(landing["landingblockSet"]))
            for block in landing["landingblockSet"]:
                self.assertEqual(2, len(block["slides"]))
                self.assertEqual(2, len(block["twoColumnItems"]))
                self.assertEqual(2, len(block["digitItems"]))
                self.assertEqual(2, len(block["advantages"]))
                self.assertEqual(2, len(block["steps"]))
                self.assertEqual(3, len(block["progressSet"]))
                self.assertEqual(2, len(block["listItems"]))

    def test_landing_blocks(self):
        landing = LandingFactory()
        block_1 = LandingBlockFactory(landing=landing, block_type=LandingBlockChoices.ONE_IMAGE)
        block_2 = LandingBlockFactory(landing=landing, block_type=LandingBlockChoices.TWO_IMAGE)
        block_3 = LandingBlockFactory(landing=landing, block_type=LandingBlockChoices.THREE_IMAGE)

        query = """
        query {
            landingBlock(id: "%s") {
                id
            }
        }
        """

        resp = self.query(query % to_global_id(LandingBlockType.__name__, block_1.id))
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()["data"]

        self.assertEqual(1, len(resp_data))
        self.assertEqual(str(block_1.id), resp_data["landingBlock"]["id"])

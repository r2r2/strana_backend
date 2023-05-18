import json
from common.test_cases import BaseTestCase
from .factories import (
    MainPageFactory,
    MainPageSlideFactory,
    MainPageIdeologyCardFactory,
    MapTextFactory,
    MainPageStoryFactory,
    MainPageStoryImageFactory,
)


class MainPageQueryTest(BaseTestCase):
    maxDiff = None

    def test_main_page(self):
        pages = [MainPageFactory() for _ in range(2)]
        page = pages[0]
        stories = [MainPageStoryFactory(page=page) for i in range(4)]
        for story in stories:
            images = [MainPageStoryImageFactory() for _ in range(4)]
            story.images.add(*images)
        slides = [MainPageSlideFactory(page=page, is_active=i % 2 == 0) for i in range(10)]
        active_slides = [s for s in slides if s.is_active is True]
        cards = [MainPageIdeologyCardFactory(page=page) for _ in range(4)]
        map_texts = [MapTextFactory() for _ in range(4)]

        for map_text in map_texts:
            page.map_texts.add(map_text)

        query = """
                query {
                    mainPage {
                        id
                        slides {
                            title
                        }
                        ideologyCards {
                            title
                        }
                        mapTexts {
                            text
                        }
                        stories {
                            name
                            fileDisplay
                            filePreview
                            images {
                                text
                                fileDisplay
                                filePreview
                            }
                        }
                    }
                }
                """

        with self.assertNumQueries(6):
            response = self.query(query)
        self.assertResponseNoErrors(response)
        data = json.loads(response.content)
        page_data = data["data"]["mainPage"]
        slides_data = page_data["slides"]

        self.assertResponseNoErrors(response)
        self.assertEqual(len(slides_data), len(active_slides))
        for i in range(len(active_slides)):
            self.assertEqual(slides_data[i]["title"], active_slides[i].title)

        cards_data = page_data["ideologyCards"]
        self.assertEqual(len(cards_data), len(cards))
        for i in range(len(cards)):
            self.assertEqual(cards_data[i]["title"], cards[i].title)

        map_texts_data = page_data["mapTexts"]
        self.assertEqual(len(map_texts_data), len(map_texts))
        for i in range(len(map_texts_data)):
            self.assertEqual(map_texts_data[i]["text"], map_texts[i].text)

        stories_data = page_data["stories"]
        self.assertEqual(len(stories_data), len(stories))
        for i in range(len(stories_data)):
            self.assertEqual(stories_data[i]["name"], stories[i].name)
            self.assertEqual(len(stories_data[i]["images"]), stories[i].images.count())

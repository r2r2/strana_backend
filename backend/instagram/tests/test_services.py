from unittest.mock import patch

from django.test import TestCase
from requests import Session

from instagram.services import scrape_posts_instagram, update_post
from ..factories import InstagramPostFactory, InstagramAccountFactory
from ..models import InstagramPost

GET_POST = {
    "data": {"shortcode_media": {"edge_media_preview_like": {"count": 42, "edges": []}}},
}

GET_POSTS = {
    "data": {
        "user": {
            "edge_owner_to_timeline_media": {
                "edges": [
                    {
                        "node": {
                            "__typename": "GraphImage",
                            "id": "2329244848043350818",
                            "display_url": "",
                            "shortcode": "CBTI9kyiFsi",
                            "taken_at_timestamp": 1591887645,
                            "edge_media_to_caption": {
                                "edges": [
                                    {
                                        "node": {
                                            "text": "Кто может знать о домах Страны больше, чем сотрудник компании?\n⠀\nCегодня наш герой — специалист по продаже недвижимости Анна Алтухова, которая выбрала для себя и своей семьи Звездный👇🏻\n⠀\n🌟Как узнала про Звездный\nЯ узнала о Стране из рекламы сайта пару лет назад. Просто переходила по страницам и наткнулась на баннер Звездного. Меня впечатлил визуал комплекса и очень привлекла масштабность проекта.\n⠀\n🌟Что повлияло на выбор\nМы с ребенком приехали, прогулялись, и уже тогда я ощутила тот комфорт и уют, который Звездный предлагает жителям. Мне было очень важно, чтобы комфортно и безопасно было не только мне, но и моему ребенку — эти моменты я для себя сразу отметила. У меня даже не возникало мысли рассмотреть других застройщиков — достаточно было просто увидеть, что сейчас построено.\n⠀\n🌟За что любить Звездный\n1. Уют. Когда вы заезжаете, вы сразу ощущаете эту особую атмосферу, которая вас притягивает.\n2. Евроформат. На тот момент планировки с большой кухней-гостиной были только в Звездном, да и сейчас таких предложений не так много.\n3. Концепция самого микрорайона. Город в городе — вся инфраструктура рядом.\n⠀\n🌟Мой совет\nВ Звездный нужно приехать и увидеть всё своими глазами. И обязательно возьмите детей!\n⠀\n#живу_в_Стране #звёздный_городок"
                                        }
                                    }
                                ]
                            },
                            "edge_media_preview_like": {"count": 223, "edges": []},
                        }
                    },
                    {
                        "node": {
                            "__typename": "GraphSidecar",
                            "id": "2326372761486233794",
                            "display_url": "",
                            "edge_media_to_caption": {
                                "edges": [
                                    {
                                        "node": {
                                            "text": "Кто может знать о домах Страны больше, чем сотрудник компании?\n⠀\nCегодня наш герой — специалист по продаже недвижимости Анна Алтухова, которая выбрала для себя и своей семьи Звездный👇🏻\n⠀\n🌟Как узнала про Звездный\nЯ узнала о Стране из рекламы сайта пару лет назад. Просто переходила по страницам и наткнулась на баннер Звездного. Меня впечатлил визуал комплекса и очень привлекла масштабность проекта.\n⠀\n🌟Что повлияло на выбор\nМы с ребенком приехали, прогулялись, и уже тогда я ощутила тот комфорт и уют, который Звездный предлагает жителям. Мне было очень важно, чтобы комфортно и безопасно было не только мне, но и моему ребенку — эти моменты я для себя сразу отметила. У меня даже не возникало мысли рассмотреть других застройщиков — достаточно было просто увидеть, что сейчас построено.\n⠀\n🌟За что любить Звездный\n1. Уют. Когда вы заезжаете, вы сразу ощущаете эту особую атмосферу, которая вас притягивает.\n2. Евроформат. На тот момент планировки с большой кухней-гостиной были только в Звездном, да и сейчас таких предложений не так много.\n3. Концепция самого микрорайона. Город в городе — вся инфраструктура рядом.\n⠀\n🌟Мой совет\nВ Звездный нужно приехать и увидеть всё своими глазами. И обязательно возьмите детей!\n⠀\n#живу_в_Стране #звёздный_городок"
                                        }
                                    }
                                ]
                            },
                            "shortcode": "CBI77NviBDC",
                            "taken_at_timestamp": 1591545265,
                            "edge_media_preview_like": {"count": 86, "edges": []},
                            "edge_sidecar_to_children": {
                                "edges": [
                                    {
                                        "node": {
                                            "__typename": "GraphImage",
                                            "id": "2326372755672963175",
                                            "display_url": "",
                                        }
                                    },
                                    {
                                        "node": {
                                            "__typename": "GraphImage",
                                            "id": "2326372755689774332",
                                            "display_url": "",
                                        }
                                    },
                                ]
                            },
                        }
                    },
                ]
            }
        }
    }
}


class MockResponse:
    def __init__(self, json_data, status_code, cookies):
        self.json_data = json_data
        self.status_code = status_code
        self.cookies = cookies

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return


def mocked_scrape_posts_instagram(*args, **kwargs):

    if args[0] == "https://www.instagram.com/":
        return MockResponse({}, 200, {"csrftoken": 1})
    elif (
        args[0]
        == """https://www.instagram.com/graphql/query/?query_hash=eddbde960fed6bde675388aac39a3657&variables={"id":"3241043704","first":12}"""
    ):
        return MockResponse(GET_POSTS, 200, {"csrftoken": 1})

    return MockResponse(None, 404, {"csrftoken": 1})


def mocked_update_post(*args, **kwargs):

    if args[0] == "https://www.instagram.com/":
        return MockResponse({}, 200, {"csrftoken": 1})
    elif (
        args[0]
        == """https://www.instagram.com/graphql/query/?query_hash=8061d8ba6866a69b02600d467920ed5c&variables={"shortcode":"123"}"""
    ):
        return MockResponse(GET_POST, 200, {"csrftoken": 1})

    return MockResponse(None, 404, {"csrftoken": 1})


class ServiceTest(TestCase):
    @patch.object(Session, "get", side_effect=mocked_scrape_posts_instagram)
    def test_scrape_posts_instagram(self, mock_session_get):
        account = InstagramAccountFactory()
        account.id = 3241043704
        account.first = 12
        account.save()
        scrape_posts_instagram(account.id, account.first)
        self.assertEqual(InstagramPost.objects.count(), 2)

    @patch.object(Session, "get", side_effect=mocked_update_post)
    def test_update_post(self, mock_session_get):
        p = InstagramPostFactory(shortcode="123", likes=0)
        update_post("123")
        p.refresh_from_db()
        self.assertEqual(p.likes, 42)

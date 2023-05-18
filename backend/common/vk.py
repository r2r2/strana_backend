import requests
from django.conf import settings

BASE_URL = "https://api.vk.com/method/"
POST_URL = (BASE_URL + 'wall.getById/')
POSTS_URL = (BASE_URL + 'wall.get/')
CHROME_WIN_UA = "Mozilla/5.0 (Windows NT 10.0; WOW64)" \
                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"


class VkScraper(object):
    def __init__(self, **kwargs):
        self.params = {
            "access_token": settings.VK_TOKEN,
            "domain": "strana_com",
            "count": 50,
            "v": "5.131"
        }
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers = {"user-agent": CHROME_WIN_UA}

    def get_posts(self, offset: int = 0):
        """ Получение постов """
        url = POSTS_URL
        self.params['offset'] = offset
        req = self.session.get(url, params=self.params)
        req.raise_for_status()
        return req.json()

    def get_post(self, post: str):
        """ Получение одного поста """
        url = POST_URL
        self.params['posts'] = post
        req = self.session.get(url, params=self.params)
        req.raise_for_status()
        return req.json()

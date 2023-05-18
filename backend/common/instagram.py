import requests

BASE_URL = "https://www.instagram.com/"
POST_URL = (
    BASE_URL
    + 'graphql/query/?query_hash=8061d8ba6866a69b02600d467920ed5c&variables={"shortcode":"%s"}'
)
POSTS_URL = (
    BASE_URL
    + 'graphql/query/?query_hash=eddbde960fed6bde675388aac39a3657&variables={"id":"%s","first":%s}'
)
STORIES_UA = "Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15"
CHROME_WIN_UA = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"


class InstagramScraper(object):
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.session.verify = False

        self.session.headers = {"user-agent": CHROME_WIN_UA}
        self.session.cookies.set("ig_pr", "1")

    def authenticate(self):
        self.session.headers.update(
            {"Referer": BASE_URL, "user-agent": STORIES_UA,}
        )
        req = self.session.get(BASE_URL)
        req.raise_for_status()
        self.session.headers.update({"X-CSRFToken": req.cookies["csrftoken"]})

        self.session.headers.update({"user-agent": CHROME_WIN_UA})
        self.rhx_gis = ""
        self.authenticated = True

    def get_posts(self, id="3241043704", first=12):
        """ Получение постов """
        url = POSTS_URL % (id, first)
        req = self.session.get(url)
        req.raise_for_status()
        return req.json()

    def get_post(self, short_code="CAVV5yiiOGM"):
        """ Получение одного поста """
        url = POST_URL % (short_code)
        req = self.session.get(url)
        req.raise_for_status()
        return req.json()

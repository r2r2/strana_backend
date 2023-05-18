from django.contrib.sitemaps import Sitemap


class SitemapMeta(type):
    """
    Добавляет внутренние классы в список элементов sitemap
    """

    def __new__(cls, name, bases, attrs):
        maps = dict()
        for name, attr in attrs.items():
            if (
                not isinstance(attr, str)
                and attr.__name__.lower().count("sitemap")
                and getattr(attr, "name", None) is not None
            ):
                maps[attr.name] = attr
        attrs["maps"] = maps
        return super().__new__(cls, name, bases, attrs)


class BaseSitemap(Sitemap):
    """
    Sitemap с базовой конфигурацией
    """

    name = None
    objects = None
    changefreq = "weekly"
    priority = 1.0

    def __init__(self, request):
        self.request = request

    def items(self):
        return self.objects

    def location(self, obj):
        return f"/{self.name}/{obj}/"

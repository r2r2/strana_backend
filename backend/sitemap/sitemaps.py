from graphql_relay import to_global_id
from news.models import News
from projects.models import Project
from properties.constants import PropertyType
from properties.models import Property
from properties.schema import GlobalFlatType, GlobalCommercialSpaceType
from purchase.models import PurchaseTypeCategory
from sitemap.bases import SitemapMeta, BaseSitemap


class StranaSitemap(object, metaclass=SitemapMeta):
    """
    Sitemap страны
    """

    class StaticSitemap(BaseSitemap):
        """
        Карта статических страниц
        """

        name = "static"
        objects = [
            "about",
            "about/partners",
            "about/vacancy",
            "commercial",
            "commercial/filter",
            "contacts",
            "documents",
            "favorites",
            "flats",
            "mass-media",
            "parking",
            "projects",
            "purchase",
            "purchase/mortgage",
        ]

        def location(self, obj):
            return f"/{obj}/"

    class CommercialSitemap(BaseSitemap):
        """
        Карта коммерческих страниц
        """

        name = "commercial"

        def items(self):
            ids = (
                Property.objects.filter_active()
                .filter(type=PropertyType.COMMERCIAL)
                .filter_current_site(self.request.site)
                .values_list("id", flat=True)
            )
            return [to_global_id(GlobalCommercialSpaceType.__name__, i) for i in ids]

    class FlatsSitemap(BaseSitemap):
        """
        Карта квартир
        """

        name = "flats"

        def items(self):
            ids = (
                Property.objects.filter_active()
                .filter(type=PropertyType.FLAT)
                .filter_current_site(self.request.site)
                .values_list("id", flat=True)
            )
            return [to_global_id(GlobalFlatType.__name__, i) for i in ids]

    class NewsSitemap(BaseSitemap):
        """
        Карта новостей
        """

        name = "news"

        def items(self):
            slugs = (
                News.objects.active()
                .filter(projects__city__site=self.request.site)
                .order_by("slug")
                .distinct("slug")
                .values_list("slug", flat=True)
            )
            return slugs

    class ProjectsSitemap(BaseSitemap):
        """
        Карта проектов
        """

        name = "projects"

        def items(self):
            slugs = (
                Project.objects.filter_active()
                .filter(city__site=self.request.site)
                .values_list("slug", flat=True)
            )
            return slugs

    class PromoSitemap(BaseSitemap):
        """
        Карта промо
        """

        name = "promo"

        def items(self):
            slugs = (
                News.objects.active()
                .filter(projects__city__site=self.request.site)
                .order_by("slug")
                .distinct("slug")
                .values_list("slug", flat=True)
            )
            return slugs

    class PurchaseSitemap(BaseSitemap):
        """
        Карта покупок
        """

        name = "purchase"

        def items(self):
            slugs = (
                PurchaseTypeCategory.objects.filter(is_active=True)
                .filter(purchasetype__city__site=self.request.site)
                .values_list("slug", flat=True)
            )
            return slugs

import datetime
from calendar import timegm
from django.contrib.sitemaps.views import x_robots_tag
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.http import http_date
from common.utils import make_hash_sha256
from .sitemaps import StranaSitemap


@x_robots_tag
def sitemap(request):
    """
    Получение sitemap
    """
    template = "common/sitemap/sitemap.xml"
    content_type = "application/xml"

    request_protocol = request.scheme
    request_site = request.site
    sitemaps = StranaSitemap.maps

    cache_raw = "sitemap" + request_site.domain
    cache_name = make_hash_sha256(cache_raw)

    maps = sitemaps.values()

    page = request.GET.get("p", 1)
    all_sites_lastmod = True
    lastmod = None
    urls = []

    context = cache.get(cache_name)

    if context:

        response = TemplateResponse(request, template, context, content_type)

        if all_sites_lastmod and lastmod is not None:
            response["Last-Modified"] = http_date(timegm(lastmod))

        return response

    for site in maps:

        try:

            if callable(site):
                site = site(request)
            urls.extend(site.get_urls(page=page, site=request_site, protocol=request_protocol))

            if all_sites_lastmod:
                site_lastmod = getattr(site, "latest_lastmod", None)
                if site_lastmod is not None:
                    site_lastmod = (
                        site_lastmod.utctimetuple()
                        if isinstance(site_lastmod, datetime.datetime)
                        else site_lastmod.timetuple()
                    )
                    lastmod = site_lastmod if lastmod is None else max(lastmod, site_lastmod)
                else:
                    all_sites_lastmod = False

        except EmptyPage:

            raise Http404("Page %s empty" % page)

        except PageNotAnInteger:

            raise Http404("No page '%s'" % page)

    context = {"urlset": urls}

    response = TemplateResponse(request, template, context, content_type)

    if all_sites_lastmod and lastmod is not None:

        response["Last-Modified"] = http_date(timegm(lastmod))

    cache.set(cache_name, context, 300)

    return response

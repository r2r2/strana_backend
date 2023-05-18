from urllib.parse import urlencode

from django.contrib.sites.models import Site
from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import Abs, Power, Sqrt
from django.http import HttpResponseRedirect

from app.settings import DEFAULT_SITE_URL_REDIRECT, SESSION_COOKIE_DOMAIN
from common.utils import get_client_ip

from .services import get_location


def location(request, *args, **kwargs):
    """
    Редиректит на сайт близжайшего города
    При заходе на DEFAULT_SITE_HOST
    """
    redirect = request.session.get("redirect", None)

    path = request.path
    scheme = request.scheme
    query_string = "?" + urlencode(request.GET)

    if redirect:
        redirect += path
        return HttpResponseRedirect(redirect)

    client_ip = get_client_ip(request)
    geo = get_location(client_ip)
    if not geo or not geo.site:
        redirect = DEFAULT_SITE_URL_REDIRECT
        redirect += path
        redirect += query_string
        return make_redirect_response(redirect)
    site = geo.site
    redirect = scheme + "://" + site.domain
    request.session["redirect"] = redirect
    redirect += path
    redirect += query_string
    return make_redirect_response(redirect)


def make_redirect_response(redirect):
    response = HttpResponseRedirect(redirect)
    response.set_cookie(key="city_guessed_or_default", value=True, domain=SESSION_COOKIE_DOMAIN)
    return response

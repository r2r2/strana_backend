from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from app.views import ExtraCachingGraphQLView
from company.views import StableDocumentDetailView
from feeds.views import FeedDetailView
from location.views import location
from panel_manager.admin_site import panel_site
from panel_manager.routers import panel_manager_router
from panel_manager.viewsets import WebHookViewSet
from sitemap.views import sitemap

urlpatterns = [
    path("admin/ckeditor/", include("ckeditor_uploader.urls")),
    path("admin/", include("ajaximage.urls")),
    path("admin/", admin.site.urls),
    path("admin/panel/", panel_site.urls),
    path("graphql/", csrf_exempt(ExtraCachingGraphQLView.as_view(graphiql=True))),
    path("robots.txt", include("robots.urls")),
    path("sitemap.xml", sitemap, name="sitemap"),
    path("feed/<slug:template_slug>/<slug:slug>/", FeedDetailView.as_view()),
    path("file/<slug:slug>/", StableDocumentDetailView.as_view(), name="stable_file"),
    path("api/panel/", include(panel_manager_router.urls)),
    path("api/panel/web_hook_meeting/", csrf_exempt(WebHookViewSet.as_view())),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    re_path(r".*", location),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("api/__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += staticfiles_urlpatterns()

admin.site.site_header = "Администрирование сайта Страна Девелопмент"
admin.site.site_title = "Страна Девелопмент"

from django.contrib import admin
from django.urls import include, path

from admin.config.settings import DEBUG

urlpatterns = [
    path("admin/ckeditor/", include("ckeditor_uploader.urls")),
    path('admin/logs/', include('log_viewer.urls')),
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path('admin/', admin.site.urls),
    path('admin/', include('users.urls')),
]
if DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

admin.site.site_header = "Администрирование ЛК Страна Девелопмент"
admin.site.site_title = "ЛК Страна Девелопмент"
